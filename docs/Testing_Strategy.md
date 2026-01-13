# Testing Strategy

## Overview

We manually tested the application by running the app with various user scenarios The purpose was to ensure that all of the key features functioned as intended and that errors were handled appropriately. By replicating actual user interactions, testing was done out via the command-line interface.

## Test Scenarios

### Authentication Testing
- Creating new customer accounts with valid/invalid credentials 
- Logging in with user ID and password
- Logging in with email address and password
- Testing with wrong passwords
- Trying to sign up with duplicate email addresses

### Customer Features Testing

Note: Many edge cases for these features are covered in the Error Handling section.

**Product Search**
- Searching with valid keywords i,e.. name, category or description
- Testing pagination through multiple pages of results
- Viewing further product details from search results

**Shopping Cart**
- Adding products to cart
- Viewing cart contents
- Updating item quantities
- Removing items from cart
- Adding multiple items to cart

**Checkout Process**
- Placing orders with sufficient stock beforehand
- Attempting to checkout when stock is insufficient (order count > stock count)
- Verifying stock reduction after successful orders by viewing product details after checkout
- Confirming cart is emptied after checkout 
- Testing with empty cart
- NOTE: carts are linked to sessions, i.e.. they will be emptied if we open a new session. This is largely due to schema definition of cart where we store sessionNo as part of the primary key.

**Order History**
- Viewing order history
- Viewing detailed order information when prompted
- Testing with customers who have no prior orders

### Sales Agent Features Testing

Note: Many edge cases for these features are covered in the Error Handling section.

**Product Updates**
- Updating product prices with valid and invalid values
- Updating stock counts
- Testing with invalid product IDs
- Testing with negative prices 
- Testing with negative stock 
- Testing with non-numeric inputs

**Sales Reports**
- Generating weekly sales report
- Verifying calculations for the report manually by checking the database using sqlite extension
- Testing when no orders were placed in the last week

**Top Products**
- Viewing top products by order count
- Viewing top products by view count
- Testing with products that have equal order or view counts

### Session Tracking
- Verifying if session is tracked when customer logs in
- Checking that activities are recorded with the responding session numbers
- Confirming sessions end on logout and are recorded in the tables

### Error Handling
- Testing all menu options with all sorts of invalid inputs
- Trying to access non-existent products for details and updates depending on the role
- Testing numeric fields with non-numeric input as well
- Signing up with an email address that is already registered
- Signing up with empty name/email/password fields
- Entering an invalid email format (missing '@' or '.')
- Logging in with non-existent user ID or email; wrong password
- Trying SQL injection payloads in login, search, and product update inputs
- Submitting blank search keyword; verify case-insensitive matches and multi-keyword AND semantics
- Entering non-numeric values for numeric fields (pid, qty, price, stock)
- Entering negative or zero values where not allowed (qty, price)
- Entering extremely large numbers (qty > stock, very large price)
- Pagination edge cases: Next on last page, Prev on first page, non-digit selection, out-of-range indexes
- Cart edge cases: updating qty to exceed stock, setting qty to zero, removing an item not in cart
- Checkout edge cases: empty shipping address, excessively long address, declining confirmation, empty cart
- Orders edge cases: selecting invalid index, requesting details for a non-existent order
- Sales update edge cases: non-existent product ID, negative/zero price, non-integer stock
- Launching with invalid DB file path; program handles this gracefully

## Bugs Found and Fixed

### Database Schema Issues
**Problem**: Tables were being recreated on every run, causing errors if they already existed.  
**Fix**: Added `IF NOT EXISTS` to all CREATE TABLE statements in `db.py`.

### Cart Session Dependency
**Problem**: Cart is emptied when the customer logs out and starts a new session by loggin in, this is due the fact that the `cart` table uses sessionNo as part of its primary key. So, whenever a new session is created the previous cart is not visible anymore to the customer.
**Fix**: There is no fix, this is a design choice as provided initially in the schema (in project description on canvas) where cart(cid, sessionNo, pid, qty) and since the program autoincrements the sessionNo, we let go of the old session.

### Search AND semantics
**Problem**: Multi-keyword search behaved like OR and missed description matches.
**Fix**: Use AND across all keywords with case-insensitive matching on `name` and `descr`.



