package sensor.server.receive;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.jms.annotation.EnableJms;

/**
 * Application to receive sensor measurements and publish them to a queue.
 */
@SpringBootApplication
@EnableJms
public class ServerReceiveDataApp {
	public static void main(String[] args) {
		SpringApplication.run(ServerReceiveDataApp.class, args);
	}
}
