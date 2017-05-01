package sensor.server.web;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class ServerWebApp {

	public static void main(String[] args) throws InterruptedException {
		Thread.sleep(15000);
		SpringApplication.run(ServerWebApp.class, args);
	}
}
