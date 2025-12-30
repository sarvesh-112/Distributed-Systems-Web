import java.rmi.Remote;
import java.rmi.RemoteException;

public interface FileService extends Remote {
    String uploadFile(String fileName, byte[] data) throws RemoteException;
}
