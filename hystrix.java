import com.netflix.hystrix.*;
import com.netflix.hystrix.strategy.concurrency.HystrixRequestContext;

import java.util.concurrent.TimeUnit;

public class hystrix {

    public static void main(String[] args) {
        HystrixRequestContext context = HystrixRequestContext.initializeContext();
        try {
            for (int i = 0; i < 100; i++) {
                System.out.println(new CommandExample("Task-" + i).execute());
            }
        } finally {
            context.shutdown();
        }
    }