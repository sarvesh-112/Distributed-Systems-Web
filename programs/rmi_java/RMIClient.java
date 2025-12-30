import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.nio.file.Files;
import java.nio.file.Paths;

public class RMIClient {
    public static void main(String[] args) {
        try {
            String filePath = args[0];
            byte[] data = Files.readAllBytes(Paths.get(filePath));

            Registry registry = LocateRegistry.getRegistry("localhost", 1099);
            FileService service = (FileService) registry.lookup("FileService");

            String result = service.uploadFile(
                Paths.get(filePath).getFileName().toString(),
                data
            );

            System.out.println(result);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
