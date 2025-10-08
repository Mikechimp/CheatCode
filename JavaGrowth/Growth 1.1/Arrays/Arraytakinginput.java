import java.util.*;

public class Arraytakinginput {
    public static void main(String[] args) {

        Scanner s = new Scanner(System.in);
        

        String[] foods;
        int size; 

        System.out.println("Num of food wanted: ");
        size = s.nextInt();
        s.nextLine();

        foods = new String[size]; 

          for(int i = 0; i < foods.length; i++) {
            System.out.println("top foods? : ");
            foods[i] = s.nextLine();
            
            
        }

     
        System.out.println();
        for(String food : foods) {
            System.out.println(food);
        }


    }
    
}
