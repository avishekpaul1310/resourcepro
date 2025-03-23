from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

def test_drag_drop_between_browser_windows(self):
    """
    Test if attempting to drag tasks between browser windows/tabs causes issues
    This simulates dragging an element and then not completing the drop operation
    """
    # Login
    self.driver.get(f'{self.live_server_url}/accounts/login/')
    self.driver.find_element(By.ID, 'id_username').send_keys('testuser')
    self.driver.find_element(By.ID, 'id_password').send_keys('testpassword')
    self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    
    # Go to allocation board
    self.driver.get(f'{self.live_server_url}/allocation/')
    
    # Find the task card
    task_card = self.driver.find_element(By.XPATH, f'//div[@data-task-id="{self.task.id}"]')
    
    # Start drag but don't drop
    action = ActionChains(self.driver)
    action.click_and_hold(task_card).perform()
    
    # Move cursor out of window (simulating moving to another tab)
    action.move_by_offset(0, -500).perform()
    
    # Release outside the window
    action.release().perform()
    
    # Navigate away and back to allocation board
    self.driver.get(f'{self.live_server_url}/dashboard/')
    self.driver.get(f'{self.live_server_url}/allocation/')
    
    # Verify the task is still available and the UI is not broken
    task_card = self.driver.find_element(By.XPATH, f'//div[@data-task-id="{self.task.id}"]')
    self.assertTrue(task_card.is_displayed())