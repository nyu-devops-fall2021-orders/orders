Feature: The order service back-end
    As a Devloper
    I need a RESTful catalog service
    So that I can keep track of all my orders

Background:
    Given the following orders
        | id         |customer_id|  tracking_id | status       |
        | 1          | 201       |  1001        | "Cancelled"  | 
        | 3          | 35        |  46          | "Cancelled"  |
        | 4          | 20        |  25          | "Created"    |
        | 5          | 34        |  45          | "Created"    |
Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Orders RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create an Order
    When I visit the "Home Page"
    And I set the "Order_id" to "1"
    And I set the "Customer_id" to "201"
    And I set the "Tracking_id" to "1001"
    And I select "Cancelled" in the "status" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Order_id" field
    And I press the "Clear" button
    Then the "Order_id" field should be empty
    And the "Customer_id" field should be empty
    And the "Tracking_id" field should be empty
    When I paste the "Order_id" field
    And I press the "Retrieve" button
    Then I should see "1" in the "Order_id" field
    And I should see "201" in the "Customer_id" field
    And I should see "1001" in the "Tracking_id" field
    And I should see "Cancelled" in the "status" dropdown

Scenario: List all orders
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "1" in the results
    And I should see "3" in the results
    And I should not see "9" in the results

Scenario: List all cancelled orders
    When I visit the "Home Page"
    And I set the "status" to "Cancelled"
    And I press the "Search" button
    Then I should see "1" in the results
    And I should not see "3" in the results
    And I should not see "4" in the results

Scenario: Update a Order
    When I visit the "Home Page"
    And I set the "Order_id" to "1"
    And I press the "Search" button
    Then I should see "201" in the "Customer_id" field
    And I should see "1001" in the "Tracking ID" field
    And I should see "Cancelled" in the "status" field
    When I change "Order ID" to "2"
    And I press the "Update" button
    Then I should see the message "Success"

Scenario: Create an Order Item
    When I visit the "Home Page"
    And I set the "order_item_id" to "1"
    And I set the "product_id" to "101"
    And I set the "quantity" to "1"
    And I set the "price" to "10.5"
    And I set the "orderid" to "1"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "order_item_id" field
    And I press the "Clear" button
    Then the "order_item_id" field should be empty
    And the "product_id" field should be empty
    And the "quantity" field should be empty
    And the "price" field should be empty
    When I paste the "order_item_id" field
    And I press the "Retrieve-item" button
    Then I should see "1" in the "order_item_id" field
    And I should see "101" in the "product_id" field
    And I should see "1" in the "quantity" field
    And I should see "10.5" in the "price" field
    And I should see "1" in the "orderid" field

Scenario: List all order items
    When I visit the "Home Page"
    And I press the "listall-item" button
    Then I should see "1" in the results
    And I should see "2" in the results
    And I should not see "9" in the results

Scenario: Update an order item
    When I visit the "Home Page"
    And I set the "order_item_id" to "1"
    And I press the "Search" button
    Then I should see "101" in the "product_id" field
    And I should see "1" in the "quantity" field
    And I should see "10.5" in the "price" field
    And I should see "1" in the "orderid" field
    When I change "order_item_id" to "4"
    And I press the "Update-item" button
    Then I should see the message "Success"



