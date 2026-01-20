import java.rmi.Remote;
import java.rmi.RemoteException;
import java.util.List;

public interface HostelService extends Remote {

    String getRoomDetails(int roomNo) throws RemoteException;

    String getWardenContact() throws RemoteException;

    List<Integer> getAllRooms() throws RemoteException;
}
