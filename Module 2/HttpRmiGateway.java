import com.sun.net.httpserver.HttpServer;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.rmi.NotBoundException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.List;

public class HttpRmiGateway {

    public static void main(String[] args) throws Exception {

        HttpServer server = HttpServer.create(new InetSocketAddress(3000), 0);

        // Endpoint: /room?no=101
        server.createContext("/room", exchange -> {

            try {
                String query = exchange.getRequestURI().getQuery(); // no=101

                if (query == null || !query.startsWith("no=")) {
                    String response = "Missing room number. Use /room?no=101";
                    exchange.sendResponseHeaders(400, response.length());
                    OutputStream os = exchange.getResponseBody();
                    os.write(response.getBytes());
                    os.close();
                    return;
                }

                int roomNo = Integer.parseInt(query.split("=")[1]);

                Registry registry = LocateRegistry.getRegistry("localhost", 1099);
                HostelService service = (HostelService) registry.lookup("HostelService");

                String result = service.getRoomDetails(roomNo);

                exchange.sendResponseHeaders(200, result.length());
                OutputStream os = exchange.getResponseBody();
                os.write(result.getBytes());
                os.close();

            } catch (NotBoundException e) {
                String response = "Service not bound in RMI registry. Start RMIServer first.";
                exchange.sendResponseHeaders(500, response.length());
                OutputStream os = exchange.getResponseBody();
                os.write(response.getBytes());
                os.close();
            } catch (Exception e) {
                String response = "Server error: " + e.getMessage();
                exchange.sendResponseHeaders(500, response.length());
                OutputStream os = exchange.getResponseBody();
                os.write(response.getBytes());
                os.close();
            }
        });

        // Optional: endpoint to list all rooms
        server.createContext("/rooms", exchange -> {
            try {
                Registry registry = LocateRegistry.getRegistry("localhost", 1099);
                HostelService service = (HostelService) registry.lookup("HostelService");

                List<Integer> rooms = service.getAllRooms();
                String result = rooms.toString();

                exchange.sendResponseHeaders(200, result.length());
                OutputStream os = exchange.getResponseBody();
                os.write(result.getBytes());
                os.close();

            } catch (Exception e) {
                String response = "Server error: " + e.getMessage();
                exchange.sendResponseHeaders(500, response.length());
                OutputStream os = exchange.getResponseBody();
                os.write(response.getBytes());
                os.close();
            }
        });

        server.start();
        System.out.println("HTTP RMI Gateway running at http://localhost:3000");
    }
}
