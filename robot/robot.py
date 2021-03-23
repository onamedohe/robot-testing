import time
from iBott.robot_activities import Robot, Queue, Item, RobotException, Robotmethod, get_all_Methods, get_instances
from iBott.browser_activities import ChromeBrowser
import robot.settings as settings


class Main(Robot):
    def __init__(self, args):
        self.methods = get_all_Methods(self)
        print(args)
        if args is not None:
            self.robotId = args['RobotId']
            self.ExecutionId = args['ExecutionId']
            self.url = args['url']
            self.username = args['username']
            self.password = args['password']
            self.robotParameters = args['params']
            super().__init__(robotId=self.robotId, ExecutionId=self.ExecutionId, url=self.url,
                             username=self.username, password=self.password,
                             params=self.robotParameters)
        else:
            super().__init__()
    @Robotmethod
    def cleanup(self):
        '''Clean system before executing the robot'''
        pass

    @Robotmethod
    def init(self):
        '''Init variables, instance objects and start the applications you are going to work with'''

        self.browser = ChromeBrowser(undetectable=True)

    @Robotmethod
    def run(self):
        '''Run robot process'''

        self.browser.open()
        self.Log.log("Chrome Browser Oppen")
        self.browser.get("http://google.com")

        if self.browser.element_exists("tag_name", "iframe"):
            iframe = self.browser.find_element_by_tag_name("iframe")
            self.browser.switch_to.frame(iframe)
            acceptButton = self.browser.find_element_by_xpath("//*[contains(text(),'Acepto')]")
            acceptButton.click()
            self.browser.switch_to.default_content()

            time.sleep(1)

            Xpathelement = "//input[@name='q']"

            # localizar el elemento
            element = self.browser.find_element_by_xpath(Xpathelement)

            # hacemos click sobre el elemento
            element.click()

            # escribirmos el texto sobre el elemento
            buscar_texto = "gatitos"
            element.send_keys(buscar_texto)
            # presionamos enter sobre el elemento
            self.browser.enter(element)
            position = 90
            self.browser.scrolldown(position)

            # localizamos los elementos con la clase "s75CSd"
            related_keywords = self.browser.find_elements_by_class_name("s75CSd")

            self.queue = Queue(self.robotId, self.url, self.token, queueName="Gatitos")

            self.Log.debug("Queue Creada satisfactoriamente")
            # Itereamos por la lista de elementos para extraer su texto
            for k in related_keywords:
                self.queue.createItem({'gatito': k.text})
                self.Log.log(k.text)

    @Robotmethod
    def end(self):
        '''Finish robot execution, cleanup enviroment, close applications and send reports'''

        self.browser.close()


class BusinessException(RobotException):
    """Manage Exceptions Caused by business errors"""

    def _init__(self,  message, action):
        super().__init__(get_instances(Main), action)
        self.action = action
        self.message = message
        self.processException()

    def processException(self):
        """Write action when a Business exception occurs"""

        self.Log.businessException(self.message)


class SystemException(RobotException):
    """Manage Exceptions Caused by system errors"""

    def __init__(self, message, action):
        super().__init__(get_instances(Main), action)
        self.retry_times = settings.RETRY_TIMES
        self.action = action
        self.message = message
        self.processException()

    def processException(self):
        """Write action when a system exception occurs"""

        self.reestart(self.retry_times)
        self.Log.systemException(self.message)

