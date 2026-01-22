import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set
import websockets
from websockets.server import WebSocketServerProtocol

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PeerServer:
    def __init__(self):
        self.peers: Dict[str, WebSocketServerProtocol] = {}
        
    async def register(self, websocket: WebSocketServerProtocol, peer_id: str):
        """Register a new peer"""
        self.peers[peer_id] = websocket
        logger.info(f"Peer registered: {peer_id}. Total peers: {len(self.peers)}")
        await self.broadcast_peers()
        
    async def unregister(self, peer_id: str):
        """Unregister a peer"""
        if peer_id in self.peers:
            del self.peers[peer_id]
            logger.info(f"Peer unregistered: {peer_id}. Total peers: {len(self.peers)}")
            await self.broadcast_peers()
    
    async def broadcast_peers(self):
        """Broadcast the list of available peers to all connected clients"""
        if not self.peers:
            return
            
        peer_list = list(self.peers.keys())
        message = json.dumps({
            "type": "peers_update",
            "peers": peer_list,
            "timestamp": datetime.now().isoformat()
        })
        
        # Send to all connected peers
        disconnected = []
        for peer_id, websocket in self.peers.items():
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(peer_id)
        
        # Clean up disconnected peers
        for peer_id in disconnected:
            await self.unregister(peer_id)
    
    async def forward_signal(self, from_peer: str, to_peer: str, signal_data: dict):
        """Forward WebRTC signaling data between peers"""
        if to_peer not in self.peers:
            logger.warning(f"Target peer {to_peer} not found")
            return False
            
        message = json.dumps({
            "type": "signal",
            "from": from_peer,
            "data": signal_data
        })
        
        try:
            await self.peers[to_peer].send(message)
            return True
        except websockets.exceptions.ConnectionClosed:
            await self.unregister(to_peer)
            return False
    
    async def handler(self, websocket: WebSocketServerProtocol):
        """Handle WebSocket connections"""
        peer_id = None
        try:
            async for message in websocket:
                data = json.loads(message)
                msg_type = data.get("type")
                
                if msg_type == "register":
                    peer_id = data.get("peer_id")
                    if peer_id:
                        await self.register(websocket, peer_id)
                        await websocket.send(json.dumps({
                            "type": "registered",
                            "peer_id": peer_id
                        }))
                
                elif msg_type == "signal":
                    to_peer = data.get("to")
                    signal_data = data.get("data")
                    if peer_id and to_peer and signal_data:
                        success = await self.forward_signal(peer_id, to_peer, signal_data)
                        if not success:
                            await websocket.send(json.dumps({
                                "type": "error",
                                "message": f"Failed to send signal to {to_peer}"
                            }))
                
                elif msg_type == "ping":
                    await websocket.send(json.dumps({"type": "pong"}))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed for peer: {peer_id}")
        except Exception as e:
            logger.error(f"Error in handler: {e}")
        finally:
            if peer_id:
                await self.unregister(peer_id)

async def main():
    server = PeerServer()
    
    async with websockets.serve(
        server.handler,
        "0.0.0.0",
        8765,
        ping_interval=20,
        ping_timeout=10
    ):
        logger.info("WebSocket server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
