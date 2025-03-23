from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
from resources.models import Resource
from projects.models import Project, Task
from django.utils import timezone
from datetime import timedelta

class ResourceProE2ETests(LiveServerTestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpassword',
            is_staff=True
        )
        
        # Create test data
        self.resource = Resource.objects.create(
            name='Test Resource',
            role='Developer',
            capacity=40
        )
        
        self.project = Project.objects.create(
            name='Test Project',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            status='active'
        )
        
        self.task = Task.objects.create(
            project=self.project,
            name='Test Task',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=10),
            estimated_hours=20,
            status='not_started'
        )
        
        # Set up Selenium
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
    
    def tearDown(self):
        self.driver.quit()
    
    def test_login_and_navigate(self):
        """Test login and navigation through app"""
        # Login
        self.driver.get(f'{self.live_server_url}/accounts/login/')
        self.driver.find_element(By.ID, 'id_username').send_keys('testuser')
        self.driver.find_element(By.ID, 'id_password').send_keys('testpassword')
        self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        
        # Verify redirect to dashboard
        WebDriverWait(self.driver, 10).until(
            EC.url_contains('/dashboard/')
        )
        
        # Navigate to projects
        self.driver.find_element(By.XPATH, '//a[contains(@href, "/projects/")]').click()
        WebDriverWait(self.driver, 10).until(
            EC.url_contains('/projects/')
        )
        
        # Verify project is listed
        self.assertTrue('Test Project' in self.driver.page_source)
    
    def test_drag_drop_allocation(self):
        """Test drag and drop functionality for allocation"""
        # Login
        self.driver.get(f'{self.live_server_url}/accounts/login/')
        self.driver.find_element(By.ID, 'id_username').send_keys('testuser')
        self.driver.find_element(By.ID, 'id_password').send_keys('testpassword')
        self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        
        # Go to allocation board
        self.driver.get(f'{self.live_server_url}/allocation/')
        
        # Find the task card and resource drop zone
        task_card = self.driver.find_element(By.XPATH, f'//div[@data-task-id="{self.task.id}"]')
        resource_zone = self.driver.find_element(By.XPATH, f'//div[@data-resource-id="{self.resource.id}"]')
        
        # Perform drag and drop with JavaScript (Selenium's drag_and_drop is unreliable)
        self.driver.execute_script('''
            function createEvent(typeOfEvent) {
                var event = document.createEvent("CustomEvent");
                event.initCustomEvent(typeOfEvent, true, true, null);
                event.dataTransfer = {
                    data: {},
                    setData: function(key, value) {
                        this.data[key] = value;
                    },
                    getData: function(key) {
                        return this.data[key];
                    }
                };
                return event;
            }
            
            function dispatchEvent(element, event, transferData) {
                if (transferData !== undefined) {
                    event.dataTransfer = transferData;
                }
                if (element.dispatchEvent) {
                    element.dispatchEvent(event);
                } else if (element.fireEvent) {
                    element.fireEvent("on" + event.type, event);
                }
            }
            
            var source = arguments[0];
            var target = arguments[1];
            
            var dragStartEvent = createEvent('dragstart');
            dispatchEvent(source, dragStartEvent);
            
            var dropEvent = createEvent('drop');
            dropEvent.dataTransfer = dragStartEvent.dataTransfer;
            dispatchEvent(target, dropEvent);
            
            var dragEndEvent = createEvent('dragend');
            dragEndEvent.dataTransfer = dragStartEvent.dataTransfer;
            dispatchEvent(source, dragEndEvent);
        ''', task_card, resource_zone)
        
        # Wait for the assignment to be created
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'assignment-card'))
        )
        
        # Verify resource utilization is updated
        utilization_text = self.driver.find_element(By.XPATH, '//span[contains(@class, "utilization-text")]').text
        self.assertTrue("%" in utilization_text)