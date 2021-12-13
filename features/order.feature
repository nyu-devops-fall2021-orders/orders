Feature: The order service back-end
    As a Devloper
    I need a RESTful catalog service
    So that I can keep track of all my orders

    Background:
        Given the following orders
            | customer_id | tracking_id | status    | product_id | quantity | price     |
            | 201         | 1001        | Cancelled | 201        | 1001     | Cancelled |
            | 35          | 46          | Cancelled | 35         | 46       | Cancelled |
            | 20          | 25          | Created   | 20         | 25       | Created   |
            | 34          | 45          | Created   | 34         | 45       | Created   |

    Scenario: The server is running
        When I visit the "Home Page"
        Then I should see "Orders RESTful Service" in the title
        And I should not see "404 Not Found"

    Scenario: Create an Order
        When I visit the "Home Page"
        And I set the "Order_id" to "1"
        And I set the "Customer_id" to "202"
        And I set the "Tracking_id" to "1002"
        And I select "Paid" in the "status" dropdown
        And I press the "Create" button
        Then I should see the message "Success"
        When I copy the "Order_id" field
        And I press the "Clear" button
        Then the "Order_id" field should be empty
        And the "Customer_id" field should be empty
        And the "Tracking_id" field should be empty
        When I paste the "Order_id" field
        And I press the "Retrieve" button
        Then I should see "202" in the "Customer_id" field
        And I should see "1002" in the "Tracking_id" field
        And I should see "Paid" in the "status" dropdown

    Scenario: List all orders
        When I visit the "Home Page"
        And I press the "listall" button
        Then I should see order for "201" in the results
        And I should not see order for "20009" in the results


    Scenario: List all cancelled orders
        When I visit the "Home Page"
        And I set the "stat" radio option
        And I set the "query" to "Cancelled"
        And I press the "Search" button
        Then I should see order for "201" in the results
        And I should not see order for "20009" in the results


    Scenario: Update a Order
        When I visit the "Home Page"
        And I press the "listall" button
        And I copy the "Order_id" field
        And I press the "clear" button
        And I paste the "Order_id" field
        And I press the "Retrieve" button
        Then I should see "201" in the "Customer_id" field
        And I should see "1001" in the "Tracking_ID" field
        And I should see "Cancelled" in the "status" field
        When I change "Customer_id" to "203"
        When I change "Tracking_ID" to "1003"
        And I select "Completed" in the "status" dropdown
        And I press the "Update" button
        Then I should see the message "Success"
        And I should see "203" in the "Customer_id" field
        And I should see "1003" in the "Tracking_ID" field
        And I should see "Completed" in the "status" field

    Scenario: Create an Order Item
        When I visit the "Home Page"
        And I press the "listall" button
        And I copy the order id in "Order_id" field
        And I press the "clear" button
        And I set the "order_item_id" to "1"
        And I set the "product_id" to "101"
        And I set the "quantity" to "1"
        And I set the "price" to "10.5"
        And I paste the order id in "orderID" field
        And I press the "Create-item" button
        Then I should see the message "Success" in items
        When I copy the "order_item_id" field
        And I press the "Clear-item" button
        Then the "order_item_id" field should be empty
        And the "product_id" field should be empty
        And the "quantity" field should be empty
        And the "price" field should be empty
        When I paste the "order_item_id" field
        And I paste the order id in "orderID" field
        And I press the "Retrieve-item" button
        Then I should see "101" in the "product_id" field
        And I should see "1" in the "quantity" field
        And I should see "10.5" in the "price" field

    Scenario: List all order items
        When I visit the "Home Page"
        And I press the "listall" button
        And I copy the order id in "Order_id" field
        And I press the "clear" button
        And I set the "order_item_id" to "1"
        And I set the "product_id" to "101"
        And I set the "quantity" to "1"
        And I set the "price" to "10.5"
        And I paste the order id in "orderID" field
        And I press the "Create-item" button
        And I press the "listall-item" button
        Then I should see order item for "101" in the item results
        And I should not see order item for "110002" in the item results

    Scenario: Update an order item
        When I visit the "Home Page"
        And I press the "listall" button
        And I copy the order id in "Order_id" field
        And I press the "clear" button
        And I set the "order_item_id" to "1"
        And I set the "product_id" to "101"
        And I set the "quantity" to "1"
        And I set the "price" to "10.5"
        And I paste the order id in "orderID" field
        And I press the "Create-item" button
        And I press the "listall-item" button
        And I copy the "Order_item_id" field
        And I copy the order id in "OrderID" field
        And I press the "clear-item" button
        And I paste the "order_item_id" field
        And I paste the order id in "OrderID" field
        And I press the "Retrieve-item" button
        Then I should see "101" in the "product_id" field
        And I should see "1" in the "quantity" field
        And I should see "10.5" in the "price" field
        When I change "quantity" to "4"
        And I press the "Update-item" button
        Then I should see the message "Success" in items
