import java.nio.file.Files;
import java.nio.file.Paths;
import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;

public class FileServiceImpl extends UnicastRemoteObject implements FileService {

    protected FileServiceImpl() throws RemoteException {
        super();
    }

    @Override
    public String uploadFile(String fileName, byte[] data) {
        try {
            String baseDir = System.getProperty("user.dir");
            String folderPath = baseDir + "/shared_data/rmi_received";

            Files.createDirectories(Paths.get(folderPath));
            Files.write(
                Paths.get(folderPath + "/received_" + fileName),
                data
            );

            return "File uploaded successfully";
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
    }
}
