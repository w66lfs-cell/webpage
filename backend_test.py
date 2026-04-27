#!/usr/bin/env python3
"""
Word of the Day App Backend API Testing Suite
Tests all backend endpoints in the specified order with proper error handling
"""

import requests
import json
import sys
from datetime import date

# Backend URL from environment
BACKEND_URL = "https://comedy-pig-insults.preview.emergentagent.com"

# Test data
TEST_WORD = {
    "word": "Tenacious",
    "definition": "Persistent and determined, not giving up easily"
}

class BackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.created_word_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {message}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'response_data': response_data
        })
        
        if response_data:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()

    def test_1_get_all_words(self):
        """Test GET /api/words - Should return all words (5 sample words pre-populated)"""
        try:
            response = requests.get(f"{self.base_url}/api/words", timeout=10)
            
            if response.status_code == 200:
                words = response.json()
                if isinstance(words, list) and len(words) >= 5:
                    # Check if sample words exist
                    word_names = [w.get('word') for w in words]
                    expected_words = ["Serendipity", "Ephemeral", "Luminous", "Mellifluous", "Resilient"]
                    
                    found_sample_words = sum(1 for word in expected_words if word in word_names)
                    
                    self.log_result(
                        "GET /api/words",
                        True,
                        f"Retrieved {len(words)} words, including {found_sample_words} expected sample words",
                        {"word_count": len(words), "sample_words_found": found_sample_words, "words": words[:2]}  # Show first 2 words
                    )
                else:
                    self.log_result(
                        "GET /api/words",
                        False,
                        f"Expected at least 5 words, got {len(words) if isinstance(words, list) else 'invalid response'}",
                        words if isinstance(words, list) else response.text
                    )
            else:
                self.log_result(
                    "GET /api/words",
                    False,
                    f"Expected status 200, got {response.status_code}",
                    response.text
                )
                
        except requests.RequestException as e:
            self.log_result("GET /api/words", False, f"Request failed: {str(e)}")

    def test_2_add_new_word(self):
        """Test POST /api/words - Add a new word"""
        try:
            response = requests.post(
                f"{self.base_url}/api/words",
                json=TEST_WORD,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                word_data = response.json()
                if 'id' in word_data and word_data.get('word') == TEST_WORD['word']:
                    self.created_word_id = word_data['id']
                    self.log_result(
                        "POST /api/words",
                        True,
                        f"Successfully added word '{TEST_WORD['word']}' with ID: {self.created_word_id}",
                        word_data
                    )
                else:
                    self.log_result(
                        "POST /api/words",
                        False,
                        "Word added but response format is incorrect",
                        word_data
                    )
            else:
                self.log_result(
                    "POST /api/words",
                    False,
                    f"Expected status 200, got {response.status_code}",
                    response.text
                )
                
        except requests.RequestException as e:
            self.log_result("POST /api/words", False, f"Request failed: {str(e)}")

    def test_3_update_word(self):
        """Test PUT /api/words/{id} - Update the word created above"""
        if not self.created_word_id:
            self.log_result("PUT /api/words/{id}", False, "No word ID available from previous test")
            return
            
        try:
            update_data = {
                "word": "Tenacious",
                "definition": "Persistent and determined, not giving up easily. Shows great strength of purpose."
            }
            
            response = requests.put(
                f"{self.base_url}/api/words/{self.created_word_id}",
                json=update_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                word_data = response.json()
                if word_data.get('definition') == update_data['definition']:
                    self.log_result(
                        "PUT /api/words/{id}",
                        True,
                        f"Successfully updated word definition",
                        word_data
                    )
                else:
                    self.log_result(
                        "PUT /api/words/{id}",
                        False,
                        "Word updated but definition doesn't match expected value",
                        word_data
                    )
            else:
                self.log_result(
                    "PUT /api/words/{id}",
                    False,
                    f"Expected status 200, got {response.status_code}",
                    response.text
                )
                
        except requests.RequestException as e:
            self.log_result("PUT /api/words/{id}", False, f"Request failed: {str(e)}")

    def test_4_toggle_favorite(self):
        """Test PATCH /api/words/{id}/favorite - Toggle favorite on a word"""
        if not self.created_word_id:
            self.log_result("PATCH /api/words/{id}/favorite", False, "No word ID available from previous test")
            return
            
        try:
            response = requests.patch(
                f"{self.base_url}/api/words/{self.created_word_id}/favorite",
                timeout=10
            )
            
            if response.status_code == 200:
                word_data = response.json()
                if word_data.get('is_favorite') == True:
                    self.log_result(
                        "PATCH /api/words/{id}/favorite",
                        True,
                        f"Successfully toggled favorite to True",
                        word_data
                    )
                else:
                    self.log_result(
                        "PATCH /api/words/{id}/favorite",
                        False,
                        f"Expected is_favorite=True, got {word_data.get('is_favorite')}",
                        word_data
                    )
            else:
                self.log_result(
                    "PATCH /api/words/{id}/favorite",
                    False,
                    f"Expected status 200, got {response.status_code}",
                    response.text
                )
                
        except requests.RequestException as e:
            self.log_result("PATCH /api/words/{id}/favorite", False, f"Request failed: {str(e)}")

    def test_5_get_favorites(self):
        """Test GET /api/words/favorites - Get only favorited words"""
        try:
            response = requests.get(f"{self.base_url}/api/words/favorites", timeout=10)
            
            if response.status_code == 200:
                favorites = response.json()
                if isinstance(favorites, list):
                    # Check if our favorited word is in the list
                    favorited_word_found = False
                    if self.created_word_id:
                        favorited_word_found = any(
                            word.get('id') == self.created_word_id and word.get('is_favorite') == True 
                            for word in favorites
                        )
                    
                    self.log_result(
                        "GET /api/words/favorites",
                        True,
                        f"Retrieved {len(favorites)} favorite words. Test word found: {favorited_word_found}",
                        {"favorite_count": len(favorites), "test_word_found": favorited_word_found, "favorites": favorites}
                    )
                else:
                    self.log_result(
                        "GET /api/words/favorites",
                        False,
                        "Response is not a list",
                        response.text
                    )
            else:
                self.log_result(
                    "GET /api/words/favorites",
                    False,
                    f"Expected status 200, got {response.status_code}",
                    response.text
                )
                
        except requests.RequestException as e:
            self.log_result("GET /api/words/favorites", False, f"Request failed: {str(e)}")

    def test_6_word_of_day(self):
        """Test GET /api/word-of-day - Get random word of the day (should return same word if called again same day)"""
        try:
            # First call
            response1 = requests.get(f"{self.base_url}/api/word-of-day", timeout=10)
            
            if response1.status_code != 200:
                self.log_result(
                    "GET /api/word-of-day",
                    False,
                    f"First call failed with status {response1.status_code}",
                    response1.text
                )
                return
            
            word1 = response1.json()
            
            # Second call (should return same word)
            response2 = requests.get(f"{self.base_url}/api/word-of-day", timeout=10)
            
            if response2.status_code != 200:
                self.log_result(
                    "GET /api/word-of-day",
                    False,
                    f"Second call failed with status {response2.status_code}",
                    response2.text
                )
                return
            
            word2 = response2.json()
            
            # Check if both calls return the same word
            if word1.get('id') == word2.get('id') and word1.get('word') == word2.get('word'):
                self.log_result(
                    "GET /api/word-of-day",
                    True,
                    f"Word of the day consistency verified: '{word1.get('word')}'",
                    {"first_call": word1, "second_call_same": True}
                )
            else:
                self.log_result(
                    "GET /api/word-of-day",
                    False,
                    "Word of the day returned different words on consecutive calls",
                    {"first_call": word1, "second_call": word2}
                )
                
        except requests.RequestException as e:
            self.log_result("GET /api/word-of-day", False, f"Request failed: {str(e)}")

    def test_7_delete_word(self):
        """Test DELETE /api/words/{id} - Delete the test word created"""
        if not self.created_word_id:
            self.log_result("DELETE /api/words/{id}", False, "No word ID available from previous test")
            return
            
        try:
            response = requests.delete(f"{self.base_url}/api/words/{self.created_word_id}", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('message') == "Word deleted successfully":
                    self.log_result(
                        "DELETE /api/words/{id}",
                        True,
                        f"Successfully deleted test word with ID: {self.created_word_id}",
                        result
                    )
                    
                    # Verify word is actually deleted
                    verify_response = requests.get(f"{self.base_url}/api/words", timeout=10)
                    if verify_response.status_code == 200:
                        words = verify_response.json()
                        word_still_exists = any(word.get('id') == self.created_word_id for word in words)
                        if not word_still_exists:
                            print(f"✅ Verified - Word no longer exists in database")
                        else:
                            print(f"⚠️  Warning - Word still found in database after deletion")
                else:
                    self.log_result(
                        "DELETE /api/words/{id}",
                        False,
                        f"Unexpected response message: {result.get('message')}",
                        result
                    )
            else:
                self.log_result(
                    "DELETE /api/words/{id}",
                    False,
                    f"Expected status 200, got {response.status_code}",
                    response.text
                )
                
        except requests.RequestException as e:
            self.log_result("DELETE /api/words/{id}", False, f"Request failed: {str(e)}")

    def test_error_handling(self):
        """Test error handling with invalid data"""
        print("=== TESTING ERROR HANDLING ===\n")
        
        # Test invalid ObjectId on PUT endpoint
        try:
            response = requests.put(
                f"{self.base_url}/api/words/invalid_id",
                json={"word": "test"},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code == 400:
                self.log_result(
                    "Error Handling - Invalid ObjectId",
                    True,
                    "Correctly returned 400 for invalid ObjectId",
                    response.json()
                )
            else:
                self.log_result(
                    "Error Handling - Invalid ObjectId",
                    False,
                    f"Expected 400, got {response.status_code}",
                    response.text
                )
        except requests.RequestException as e:
            self.log_result("Error Handling - Invalid ObjectId", False, f"Request failed: {str(e)}")

        # Test 404 for non-existent word
        try:
            response = requests.put(
                f"{self.base_url}/api/words/507f1f77bcf86cd799439011",  # Valid ObjectId format but non-existent
                json={"word": "test"},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code == 404:
                self.log_result(
                    "Error Handling - Non-existent Word",
                    True,
                    "Correctly returned 404 for non-existent word",
                    response.json()
                )
            else:
                self.log_result(
                    "Error Handling - Non-existent Word",
                    False,
                    f"Expected 404, got {response.status_code}",
                    response.text
                )
        except requests.RequestException as e:
            self.log_result("Error Handling - Non-existent Word", False, f"Request failed: {str(e)}")

    def run_all_tests(self):
        """Run all tests in the specified order"""
        print("=" * 80)
        print("WORD OF THE DAY APP - BACKEND API TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Date: {date.today().isoformat()}")
        print()
        
        # Run tests in specified order
        self.test_1_get_all_words()
        self.test_2_add_new_word()
        self.test_3_update_word()
        self.test_4_toggle_favorite()
        self.test_5_get_favorites()
        self.test_6_word_of_day()
        self.test_7_delete_word()
        
        # Additional error handling tests
        self.test_error_handling()
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print()
        
        if failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['message']}")
            print()
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Success Rate: {success_rate:.1f}%")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)