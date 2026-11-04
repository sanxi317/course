
import java.rmi.Naming;

public class CalculatorClient {
    public static void main(String[] args) {
        try {
            String host = args.length > 0
                    ? args[0] : "localhost";

            Calculator calc = (Calculator) Naming.lookup(
                "rmi://" + host + ":1099/Calculator"
            );

            System.out.println("Connected to RMI Server!");

            System.out.println("10 + 5 = " + calc.add(10, 5));
            System.out.println("10 - 5 = " + calc.sub(10, 5));
            System.out.println("10 * 5 = " + calc.mul(10, 5));
            System.out.println("10 / 5 = " + calc.div(10, 5));

            try {
                calc.div(10, 0);
            } catch (IllegalArgumentException e) {
                System.out.println("Division error: "
                        + e.getMessage());
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
