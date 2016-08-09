from base_input import BaseInputBackend


class GPIOButton(BaseInputBackend):
    def __init__(self, config):
        self.config = config
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.config.getint("SWITCH_PIN"), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.config.getint("LED_PIN"), GPIO.OUT)
        self.enable_led(False)

    def check_for_button(self):
        button_pressed = GPIO.input(self.config.getint("SWITCH_PIN"))
        if button_pressed:
            return
        pygame.display.flip()
        time.sleep(0.1)
        self.parse_events()

    def enable_led(self, mode):
        GPIO.output(self.config.getint("LED_PIN"), int(not mode))

    def cleanup(self):
        GPIO.cleanup()

