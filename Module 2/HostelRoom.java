import java.io.Serializable;
import java.util.List;

public class HostelRoom implements Serializable {

    int roomNo;
    List<String> occupants;
    String wardenContact;

    public HostelRoom(int roomNo, List<String> occupants, String wardenContact) {
        this.roomNo = roomNo;
        this.occupants = occupants;
        this.wardenContact = wardenContact;
    }
}
