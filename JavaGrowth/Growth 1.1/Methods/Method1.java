//banking program practice 
import java.util.*;

public class Method1 {
    static Scanner s = new Scanner(System.in);
    public static void main(String[] args) {
       
        double balance = 0; 
        boolean isRunning = true; 
        int choice; 
        
        //beginner banking program 
        while(isRunning){
             
        //DISPLAY MENU
        System.out.println("*************");
        System.out.println("BANKING PROGRAM");
        System.out.println("***************");
        System.out.println("1. Show Balance");
        System.out.println("2. Deposit");
        System.out.println("3. Withdraw");
        System.out.println("4. Exit");
        System.out.println("***************");

        //GET AND PROCESS USERS CHOICE 
        System.out.print("Enter your choice (1-4): ");
        choice = s.nextInt(); 

        switch(choice){
            case 1-> showBalance(balance);
            case 2-> balance += makeDeposit();
            case 3-> balance -= withdraw(balance);
            case 4-> isRunning = false;
            default -> System.out.println("Invalid Choice");

        }
    }

    System.out.print("THANK YOU HAVE A GREAT DAY"); 

        //makeDeposit()
        //withdraw()
        //EXIT MESSAGE 
        
    }

    static void showBalance(double balance){
        System.out.printf("$%.2f\n", balance);
    }

    static double makeDeposit(){
        double amount;

        System.out.print("Enter an amount to be deposited: ");
        amount = s.nextDouble();

        if(amount < 0){
            System.out.println("amount is not possible");
            return 0;
        }
        else {
            return amount; 
        }

    }

    static double withdraw(double balance){
        double amount;
        System.out.println("Enter amount to be withdraw: ");
        amount = s.nextDouble(); 

        if(amount > balance){
            System.out.println("INSUFFICIENT FUNDS");
            return 0;
        }
        else if(amount < 0){ 
            System.out.println("AMOUNT CANNOT BE NEGATIVE");
            return 0;

        }
        else {
            return amount;
        }
        

    }

    //outside main method new method must be static as our main is also static and no return type if void
}


    
//now that we are semi comfortable using methods our next primary goal is to create a confortability with implementing scannners
//we need to improve our ability with this as it seems that we cannot do it without needing to use an automated tool
//that makes it look smoother and better for ourselves. We cannat let this continue to happen. 