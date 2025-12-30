import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class RMIServer {
    public static void main(String[] args) {
        try {
            FileService service = new FileServiceImpl();
            Registry registry = LocateRegistry.createRegistry(1099);
            registry.rebind("FileService", service);
            System.out.println("RMI Server started");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
