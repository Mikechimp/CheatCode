import java.io.FileWriter;
import java.io.IOException;
import java.io.FileNotFoundException;

public class filewriter {
    public static void main(String[]args) {
        String filePath = "C:\\Users\\Mike\\OneDrive\\Desktop\\SECURITY DIVE\\CheatCode\\JavaGrowth\\Growth 1.1\\File Writing\\test.txt";
        String text = """
        I went to the store. and I bought a new friend
         He said its so fun, to go on again 
         I have been sad and alone
        in the dark 
        but once Im with you I am not torn apart. 
        """;
        try(FileWriter w = new FileWriter(filePath)){

            w.write(text);
            System.out.println("File has been written");


        }
        catch(FileNotFoundException e) {
            System.out.println("Could not locate");
        }
        catch(IOException e) {
            System.out.println("Could not write to the file");

            }

    }

}


