package uk.notnic.farmhand;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.assertEquals;

@SpringBootTest
class FarmhandApplicationTests {

	@Test
	void contextLoads() {
	}

	@Test
	void exampleTest() {
		int expected = 42;
		int actual = 42;
		assertEquals(expected, actual, "The actual value must match the expected value.");
	}
}
