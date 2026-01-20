import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class RMIServer {

    public static void main(String[] args) {
        try {
            HostelService service = new HostelServiceImpl();

            // IMPORTANT: Connect to existing rmiregistry on localhost
            Registry registry = LocateRegistry.getRegistry("localhost", 1099);

            registry.rebind("HostelService", service);

            System.out.println("Hostel RMI Server is running...");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
