package sensor.server.process;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.jms.annotation.EnableJms;

@SpringBootApplication
@EnableJms
public class ServerProcessDataApp {
	public static void main(String[] args) {
		SpringApplication.run(ServerProcessDataApp.class, args);
	}
}
