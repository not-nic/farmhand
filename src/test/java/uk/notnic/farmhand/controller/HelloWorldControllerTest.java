package uk.notnic.farmhand.controller;

import org.junit.jupiter.api.Test;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class HelloWorldControllerTest {

    @Test
    void testGetUserNotes() {
        HelloWorldController controller = new HelloWorldController();
        Authentication authentication = mock(Authentication.class);
        when(authentication.getName()).thenReturn("unit_test_user");

        ResponseEntity<String> response = controller.getUserNotes(authentication);

        assertEquals(ResponseEntity.ok("Hello unit_test_user!"), response, "The response should be 'Hello unit_test_user!'");
    }

    @Test
    void exampleTest() {
        int expected = 42;
        int actual = 42;
        assertEquals(expected, actual, "The actual value must match the expected value.");
    }
}
