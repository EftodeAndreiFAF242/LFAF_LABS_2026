#include <iostream>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <string>
#include <cstdlib>
#include <ctime>

using namespace std;

class FiniteAutomaton {
private:
    unordered_set<string> states;
    unordered_set<char> alphabet;
    unordered_map<string, unordered_map<char, string>> transitions;
    string start_state;
    unordered_set<string> final_states;

public:
    FiniteAutomaton(
        unordered_set<string> states,
        unordered_set<char> alphabet,
        unordered_map<string, unordered_map<char, string>> transitions,
        string start_state,
        unordered_set<string> final_states
    ) {
        this->states = states;
        this->alphabet = alphabet;
        this->transitions = transitions;
        this->start_state = start_state;
        this->final_states = final_states;
    }

    bool stringBelongToLanguage(const string& input_string) {

        string current_state = start_state;

        for (char symbol : input_string) {

            if (alphabet.find(symbol) == alphabet.end())
                return false;

            if (transitions.find(current_state) == transitions.end())
                return false;

            if (transitions[current_state].find(symbol) == transitions[current_state].end())
                return false;

            current_state = transitions[current_state][symbol];
        }

        return final_states.find(current_state) != final_states.end();
    }
};

class Grammar {

private:
    unordered_set<string> non_terminals = {"S", "F", "D"};
    unordered_set<char> terminals = {'a','b','c'};
    string start_symbol = "S";

public:

    string generate_string() {

        string current = start_symbol;
        string result = "";

        while (current != "FINAL") {

            if (current == "S") {

                int choice = rand() % 2;

                if (choice == 0) {        // S → aF
                    result += 'a';
                    current = "F";
                }
                else {                   // S → bS
                    result += 'b';
                    current = "S";
                }
            }

            else if (current == "F") {

                int choice = rand() % 3;

                if (choice == 0) {       // F → bF
                    result += 'b';
                    current = "F";
                }

                else if (choice == 1) {  // F → cD
                    result += 'c';
                    current = "D";
                }

                else {                   // F → a
                    result += 'a';
                    current = "FINAL";
                }
            }

            else if (current == "D") {

                int choice = rand() % 2;

                if (choice == 0) {       // D → cS
                    result += 'c';
                    current = "S";
                }

                else {                   // D → a
                    result += 'a';
                    current = "FINAL";
                }
            }
        }

        return result;
    }

    FiniteAutomaton toFiniteAutomaton() {

        unordered_set<string> states = {"S","F","D","FINAL"};
        unordered_set<char> alphabet = {'a','b','c'};
        string start_state = "S";
        unordered_set<string> final_states = {"FINAL"};

        unordered_map<string, unordered_map<char,string>> transitions;

        transitions["S"]['a'] = "F";
        transitions["S"]['b'] = "S";

        transitions["F"]['b'] = "F";
        transitions["F"]['c'] = "D";
        transitions["F"]['a'] = "FINAL";

        transitions["D"]['c'] = "S";
        transitions["D"]['a'] = "FINAL";

        return FiniteAutomaton(
            states,
            alphabet,
            transitions,
            start_state,
            final_states
        );
    }
};

int main() {

    srand(time(NULL));

    Grammar grammar;

    cout << "Generated strings:\n";

    for (int i = 0; i < 5; i++) {
        cout << i+1 << ". " << grammar.generate_string() << endl;
    }

    FiniteAutomaton fa = grammar.toFiniteAutomaton();

    cout << "\nString validation:\n";

    vector<string> test_strings = {
        "aba",
        "abbba",
        "aca",
        "bbba",
        "acb"
    };

    for (string s : test_strings) {

        cout << s << " -> ";

        if (fa.stringBelongToLanguage(s))
            cout << "TRUE";
        else
            cout << "FALSE";

        cout << endl;
    }

    return 0;
}