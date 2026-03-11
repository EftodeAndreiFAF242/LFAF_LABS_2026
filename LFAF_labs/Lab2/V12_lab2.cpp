#include <iostream>
#include <map>
#include <set>
#include <vector>
#include <string>
#include <algorithm>
#include <iomanip>

using namespace std;

static string setToString(const set<string>& s) {
    string out;
    for (auto it = s.begin(); it != s.end(); ++it) {
        if (it != s.begin()) out += ",";
        out += *it;
    }
    return out;
}

enum class ChomskyType { Type0, Type1, Type2, Type3 };

string chomskyName(ChomskyType t) {
    switch (t) {
        case ChomskyType::Type3: return "Type 3 - Regular Grammar";
        case ChomskyType::Type2: return "Type 2 - Context-Free Grammar";
        case ChomskyType::Type1: return "Type 1 - Context-Sensitive Grammar";
        default:                 return "Type 0 - Unrestricted Grammar";
    }
}

ChomskyType classifyGrammar(
    const set<string>& nonTerminals,
    const set<char>& terminals,
    const map<string, vector<string>>& productions)
{
    bool isType3 = true;
    bool isType2 = true;

    for (auto& [lhs, rhsList] : productions) {
        if (nonTerminals.find(lhs) == nonTerminals.end()) {
            isType3 = false;
            isType2 = false;
        }
        for (auto& rhs : rhsList) {
            if (isType3) {
                if (rhs.size() == 1) {
                    if (terminals.find(rhs[0]) == terminals.end())
                        isType3 = false;
                } else {
                    char first = rhs[0];
                    string rest = rhs.substr(1);
                    if (terminals.find(first) == terminals.end() ||
                        nonTerminals.find(rest) == nonTerminals.end())
                        isType3 = false;
                }
            }
        }
    }

    if (isType3) return ChomskyType::Type3;
    if (isType2) return ChomskyType::Type2;
    return ChomskyType::Type1;
}

class FiniteAutomaton {
public:
    set<string> states;
    set<char> alphabet;
    map<string, map<char, vector<string>>> transitions;
    string startState;
    set<string> finalStates;

    FiniteAutomaton() = default;
    FiniteAutomaton(set<string> states, set<char> alphabet,
                    map<string, map<char, vector<string>>> transitions,
                    string startState, set<string> finalStates)
        : states(move(states)), alphabet(move(alphabet)),
          transitions(move(transitions)), startState(move(startState)),
          finalStates(move(finalStates)) {}

    map<string, vector<string>> toRegularGrammar() const {
        map<string, vector<string>> productions;
        for (auto& [state, symMap] : transitions) {
            for (auto& [sym, targets] : symMap) {
                for (auto& target : targets) {
                    if (finalStates.count(target))
                        productions[state].push_back(string(1, sym));
                    else
                        productions[state].push_back(string(1, sym) + target);
                }
            }
        }
        return productions;
    }

    bool isDeterministic() const {
        for (auto& [state, symMap] : transitions)
            for (auto& [sym, targets] : symMap)
                if (targets.size() > 1) return false;
        return true;
    }

    FiniteAutomaton toDFA() const {
        auto stateName = [](const set<string>& s) {
            return "{" + setToString(s) + "}";
        };

        set<string> dfaStates;
        map<string, map<char, vector<string>>> dfaTrans;
        set<string> dfaFinals;

        set<string> startSet = {startState};
        vector<set<string>> worklist = {startSet};
        set<set<string>> visited = {startSet};

        while (!worklist.empty()) {
            set<string> current = worklist.back();
            worklist.pop_back();
            string curName = stateName(current);
            dfaStates.insert(curName);

            for (auto& s : current)
                if (finalStates.count(s)) { dfaFinals.insert(curName); break; }

            for (char sym : alphabet) {
                set<string> next;
                for (auto& s : current) {
                    auto it = transitions.find(s);
                    if (it == transitions.end()) continue;
                    auto it2 = it->second.find(sym);
                    if (it2 == it->second.end()) continue;
                    for (auto& t : it2->second)
                        next.insert(t);
                }
                if (next.empty()) continue;
                string nextName = stateName(next);
                dfaTrans[curName][sym] = {nextName};
                if (!visited.count(next)) {
                    visited.insert(next);
                    worklist.push_back(next);
                }
            }
        }

        return FiniteAutomaton(dfaStates, alphabet, dfaTrans, stateName(startSet), dfaFinals);
    }

    void printTable(const string& title) const {
        cout << "\n" << title << "\n";
        vector<char> syms(alphabet.begin(), alphabet.end());
        sort(syms.begin(), syms.end());

        cout << left << setw(24) << "State";
        for (char s : syms) cout << left << setw(20) << string(1, s);
        cout << "\n" << string(24 + syms.size() * 20, '-') << "\n";

        vector<string> sortedStates(states.begin(), states.end());
        sort(sortedStates.begin(), sortedStates.end());

        for (auto& st : sortedStates) {
            string prefix;
            if (finalStates.count(st)) prefix += "*";
            if (st == startState) prefix += "->";
            cout << left << setw(24) << (prefix + st);
            for (char sym : syms) {
                auto it = transitions.find(st);
                if (it != transitions.end()) {
                    auto it2 = it->second.find(sym);
                    if (it2 != it->second.end() && !it2->second.empty()) {
                        set<string> tmp(it2->second.begin(), it2->second.end());
                        cout << left << setw(20) << ("{" + setToString(tmp) + "}");
                        continue;
                    }
                }
                cout << left << setw(20) << "-";
            }
            cout << "\n";
        }
    }

    void exportDOT(const string& filename, const string& title) const {
        FILE* f = fopen(filename.c_str(), "w");
        if (!f) { cerr << "Cannot open " << filename << "\n"; return; }

        fprintf(f, "digraph \"%s\" {\n", title.c_str());
        fprintf(f, "  rankdir=LR;\n");
        fprintf(f, "  node [shape=circle, style=filled, fillcolor=white];\n");

        for (auto& fs : finalStates)
            fprintf(f, "  \"%s\" [shape=doublecircle, fillcolor=\"#90ee90\"];\n", fs.c_str());

        fprintf(f, "  \"%s\" [fillcolor=\"#add8e6\"];\n", startState.c_str());
        fprintf(f, "  __start__ [shape=none, label=\"\"];\n");
        fprintf(f, "  __start__ -> \"%s\";\n", startState.c_str());

        map<pair<string, string>, vector<char>> edgeLabels;
        for (auto& [state, symMap] : transitions)
            for (auto& [sym, targets] : symMap)
                for (auto& t : targets)
                    edgeLabels[{state, t}].push_back(sym);

        for (auto& [edge, syms] : edgeLabels) {
            sort(syms.begin(), syms.end());
            string label;
            for (char c : syms) label += c;
            fprintf(f, "  \"%s\" -> \"%s\" [label=\"%s\"];\n",
                    edge.first.c_str(), edge.second.c_str(), label.c_str());
        }

        fprintf(f, "  label=\"%s\";\n  fontsize=14;\n", title.c_str());
        fprintf(f, "}\n");
        fclose(f);
        cout << "DOT file saved to " << filename << "\n";
    }
};

class Grammar {
public:
    set<string> nonTerminals;
    set<char> terminals;
    map<string, vector<string>> productions;
    string startSymbol;

    Grammar(set<string> nt, set<char> t, map<string, vector<string>> p, string s)
        : nonTerminals(move(nt)), terminals(move(t)), productions(move(p)), startSymbol(move(s)) {}

    ChomskyType classify() const {
        return classifyGrammar(nonTerminals, terminals, productions);
    }

    void print() const {
        cout << "  Non-terminals: { ";
        for (auto& nt : nonTerminals) cout << nt << " ";
        cout << "}\n  Terminals:     { ";
        for (char t : terminals) cout << t << " ";
        cout << "}\n  Start symbol:  " << startSymbol << "\n  Productions:\n";
        for (auto& [lhs, rhs] : productions) {
            cout << "    " << lhs << " -> ";
            for (size_t i = 0; i < rhs.size(); i++) {
                if (i) cout << " | ";
                cout << rhs[i];
            }
            cout << "\n";
        }
    }
};

int main() {

    set<string> states = {"q0", "q1", "q2", "q3"};
    set<char> alphabet = {'a', 'b', 'c'};
    string start = "q0";
    set<string> finals = {"q2"};

    map<string, map<char, vector<string>>> transitions = {
        {"q0", {{'b', {"q0"}}, {'a', {"q1"}}}},
        {"q1", {{'c', {"q1"}}, {'a', {"q2"}}}},
        {"q2", {{'a', {"q3"}}}},
        {"q3", {{'a', {"q1", "q3"}}}},
    };

    FiniteAutomaton fa(states, alphabet, transitions, start, finals);

    cout << "=== a) FA to Regular Grammar ===\n";
    auto prods = fa.toRegularGrammar();

    set<string> nt;
    for (auto& [s, _] : prods) nt.insert(s);

    Grammar grammar(nt, alphabet, prods, start);
    grammar.print();
    cout << "\n  Chomsky classification: " << chomskyName(grammar.classify()) << "\n";

    cout << "\n=== b) Determinism Check ===\n";
    fa.printTable("Original FA (Variant 12)");
    cout << "\n  Is deterministic: " << (fa.isDeterministic() ? "YES" : "NO") << "\n";
    if (!fa.isDeterministic())
        cout << "  Reason: delta(q3, a) = {q1, q3} - two targets for the same input.\n";

    cout << "\n=== c) NDFA -> DFA (Subset Construction) ===\n";
    FiniteAutomaton dfa = fa.toDFA();
    dfa.printTable("DFA after subset construction");
    cout << "\n  Is deterministic: " << (dfa.isDeterministic() ? "YES" : "NO") << "\n";

    cout << "\n=== d) Graphical Representation ===\n";
    fa.exportDOT("fa_original.dot", "Variant 12 - Original NDFA");
    dfa.exportDOT("fa_dfa.dot", "Variant 12 - DFA after conversion");

    return 0;
}