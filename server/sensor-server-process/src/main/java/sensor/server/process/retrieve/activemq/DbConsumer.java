package sensor.server.process.retrieve.activemq;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jms.annotation.JmsListener;
import org.springframework.stereotype.Component;

import lombok.NonNull;
import sensor.server.process.service.db.DbProcessDataService;
import sensor.server.shared.model.DeviceMeasurements;

@Component
public class DbConsumer {
	private static final Logger LOGGER = LoggerFactory.getLogger(DbConsumer.class);

	private DbProcessDataService dbProcessDataService;

	@Autowired
	public DbConsumer(@NonNull DbProcessDataService dbProcessDataService) {
		LOGGER.debug("Created active mq durable consumer with service of type {}", dbProcessDataService.getClass());
		this.dbProcessDataService = dbProcessDataService;
	}

	@JmsListener(destination = ActiveMqConfiguration.PROPERTY_TOPIC_NAME, subscription = ActiveMqConfiguration.PROPERTY_TOPIC_SUBSCRIPTION, containerFactory = ActiveMqConfiguration.DURABLE_SUBSCRIPTION)
	public void receive(DeviceMeasurements deviceMeasurements) {
		LOGGER.debug("Receiving measurements from active mq {}", deviceMeasurements);
		dbProcessDataService.process(deviceMeasurements);
	}
}
