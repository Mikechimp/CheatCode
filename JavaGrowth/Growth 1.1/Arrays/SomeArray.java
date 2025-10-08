import.java.util.*;
public class SomeArray {
    public static void main (String[] args) {
        String[] fruit = {"fruit", "fruit2", "fruit3"};
        fruit[0] = "pineapple";
        System.out.println(fruit[0]);
        Arrays.sort(fruit);
        
        int numofFruit = fruit.length; 
        System.out.println(numofFruit); 


        /*for(int i = 0; i < fruit.length; i++) {
            System.out.print(fruit[i] + " ");
        } */                                        //loop to iterate through each item in an array
        for(String fruitz : fruit){
            System.out.println(fruitz);
        }

        
        
    }
    
}
