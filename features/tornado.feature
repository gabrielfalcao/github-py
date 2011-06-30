Feature: Tornado should support github-py
  In order to get my tornado web app connected to the github API
  As a github-py maintainer
  I want to use the github-py support

  Scenario: Tornado serving urls with decorators
    Given I go to "http://localhost:9999/user"
    When I get redirected to "https://github.com/login/oauth/authorize?client_id=b2ae1ce0e63e9cbd7f9d"
    And authorize the app "github-py tornado integration test"
    Then I should be redirected back to "http://localhost:9999/user"
    And the response should match these values:
     | key   | value                  |
     | login | github-py              |
     | email | github-py@github.com   |
     | name  | Github-py library test |

