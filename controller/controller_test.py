from controller import Controller
import simple_i2c as si2c

def main():
    si2c.init_bus(1)
    myController = Controller()
    myController.simulate()
    si2c.close_bus()

if __name__ == "__main__":
    main()
