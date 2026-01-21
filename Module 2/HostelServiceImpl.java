import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;
import java.util.*;

public class HostelServiceImpl extends UnicastRemoteObject implements HostelService {

    private Map<Integer, HostelRoom> roomMap = new HashMap<>();

    protected HostelServiceImpl() throws RemoteException {
        super();

        roomMap.put(101, new HostelRoom(101, List.of("Aarav", "Rohan"), "9876543210"));
        roomMap.put(102, new HostelRoom(102, List.of("Inara", "Megha"), "9876543210"));
        roomMap.put(103, new HostelRoom(103, List.of("Kabir", "Dev"), "9876543210"));
    }

    @Override
    public String getRoomDetails(int roomNo) throws RemoteException {
        HostelRoom room = roomMap.get(roomNo);

        if (room == null) {
            return "Room not found";
        }

        return "Room_Number: " + room.roomNo +
               ", Occupants: " + room.occupants +
               ", Warden: " + room.wardenContact;
    }

    @Override
    public String getWardenContact() throws RemoteException {
        return "Hostel Warden: Mr. Sharma, Phone: 9876543210";
    }

    @Override
    public List<Integer> getAllRooms() throws RemoteException {
        return new ArrayList<>(roomMap.keySet());
    }
}
