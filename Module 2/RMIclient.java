import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class RMIclient {

    public static void main(String[] args) {
        try {
            Registry registry = LocateRegistry.getRegistry("localhost", 1099);
            HostelService service = (HostelService) registry.lookup("HostelService");

            int roomNo = Integer.parseInt(args[0]);

            String result = service.getRoomDetails(roomNo);
            System.out.println(result);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
