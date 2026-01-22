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
        roomMap.put(104, new HostelRoom(104, List.of("Priya", "Ananya"), "9876543210"));
        roomMap.put(105, new HostelRoom(105, List.of("Arjun", "Vivek"), "9876543210"));
        roomMap.put(106, new HostelRoom(106, List.of("Sahil", "Karan"), "9876543210"));
        roomMap.put(107, new HostelRoom(107, List.of("Neha", "Riya"), "9876543210"));
        roomMap.put(108, new HostelRoom(108, List.of("Aditya", "Rahul"), "9876543210"));
        roomMap.put(109, new HostelRoom(109, List.of("Sneha", "Pooja"), "9876543210"));
        roomMap.put(110, new HostelRoom(110, List.of("Manish", "Deepak"), "9876543210"));
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
