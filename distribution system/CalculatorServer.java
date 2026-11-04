
import java.rmi.Naming;

public class CalculatorServer {
    public static void main(String[] args) {
        try {
            Calculator calculator = new CalculatorImpl();

            Naming.rebind(
                "rmi://localhost:1099/Calculator",
                calculator
            );

            System.out.println("Calculator Server started!");
            System.out.println("RMI service registered.");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
