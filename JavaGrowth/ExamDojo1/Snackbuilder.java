import java.util.*;
public class Snackbuilder {
    public static void main(String[] args) {
        Scanner s = new Scanner(System.in);
        String[] snacks = new String[5]; 
        for (int i = 0; i < snacks.length; i++) {
            System.out.print("Snack " + (i + 1) + ": ");
            snacks[i] = s.nextLine().trim(); 
        }
        StringBuilder apple = new StringBuilder();
        apple.append("You have entered:");
        for (int i = 0; i < snacks.length; i++) {
            apple.append(snacks[i]);
            if (i < snacks.length -2) 
                apple.append(", ");
            else if (i == snacks.length - 2) 
                apple.append(", and ");
            else 
                apple.append(".");
        }
        System.out.println(apple.toString());
        s.close();


    }
    
}
