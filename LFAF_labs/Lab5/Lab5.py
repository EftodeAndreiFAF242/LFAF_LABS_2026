"""
Lab 5 — Chomsky Normal Form
Formal Languages & Finite Automata
Variant 12

Grammar:
  G = (V_N, V_T, P, S)
  V_N = {S, A, B, C, D, X}
  V_T = {a, b}
  P = {
    1.  S → A
    2.  A → aX
    3.  A → bX
    4.  X → ε
    5.  X → BX
    6.  X → b
    7.  B → AD
    8.  D → aD
    9.  D → a
    10. C → Ca
  }

Pipeline (5 steps):
  1. Eliminate ε-productions
  2. Eliminate renaming (unit productions)
  3. Eliminate inaccessible symbols
  4. Eliminate non-productive symbols
  5. Convert to Chomsky Normal Form
"""

from copy import deepcopy
from itertools import combinations


# ---------------------------------------------------------------------------
# Grammar representation
# ---------------------------------------------------------------------------

class Grammar:
    """
    A context-free grammar stored as:
      start    — start symbol (str)
      terminals — set of terminal symbols
      nonterminals — set of non-terminal symbols
      productions  — dict { NonTerminal: [ [symbol, ...], ... ] }
                     each production RHS is a list of symbols (str)
    """

    def __init__(self, start, terminals, nonterminals, productions):
        self.start = start
        self.terminals = set(terminals)
        self.nonterminals = set(nonterminals)
        # Deep copy so mutations don't bleed between pipeline steps
        self.productions = {k: [list(rhs) for rhs in v]
                            for k, v in productions.items()}

    def copy(self):
        return Grammar(
            self.start,
            set(self.terminals),
            set(self.nonterminals),
            self.productions,
        )

    def all_productions(self):
        """Yield (lhs, rhs) for every production."""
        for lhs, rules in self.productions.items():
            for rhs in rules:
                yield lhs, rhs

    def add_production(self, lhs, rhs):
        if lhs not in self.productions:
            self.productions[lhs] = []
        if rhs not in self.productions[lhs]:
            self.productions[lhs].append(rhs)

    def remove_production(self, lhs, rhs):
        if lhs in self.productions and rhs in self.productions[lhs]:
            self.productions[lhs].remove(rhs)

    def print(self, title="Grammar"):
        print(f"\n{'─' * 56}")
        print(f"  {title}")
        print(f"{'─' * 56}")
        print(f"  Start   : {self.start}")
        print(f"  V_N     : {{{', '.join(sorted(self.nonterminals))}}}")
        print(f"  V_T     : {{{', '.join(sorted(self.terminals))}}}")
        print(f"  Productions:")
        for lhs in sorted(self.productions):
            for rhs in self.productions[lhs]:
                rhs_str = "ε" if rhs == [] else "".join(rhs)
                print(f"    {lhs} → {rhs_str}")


# ---------------------------------------------------------------------------
# Helper: fresh non-terminal name generator
# ---------------------------------------------------------------------------

def fresh_name(existing, prefix="N"):
    i = 1
    while True:
        name = f"{prefix}{i}"
        if name not in existing:
            return name
        i += 1


# ---------------------------------------------------------------------------
# Step 1 — Eliminate ε-productions
# ---------------------------------------------------------------------------

def eliminate_epsilon(grammar: Grammar) -> Grammar:
    """
    1. Find all 'nullable' non-terminals (those that can derive ε).
    2. For every production, add all combinations where nullable symbols
       are either present or omitted (but never add a new bare ε
       unless the start symbol is nullable, in which case a special
       start rule handles it).
    3. Remove the original ε-productions.
    """
    g = grammar.copy()

    # --- find nullable set ---
    nullable = set()
    changed = True
    while changed:
        changed = False
        for lhs, rhs in g.all_productions():
            if rhs == [] and lhs not in nullable:
                nullable.add(lhs)
                changed = True
            elif all(s in nullable for s in rhs) and rhs and lhs not in nullable:
                nullable.add(lhs)
                changed = True

    print(f"\n  Nullable symbols: {nullable if nullable else '∅'}")

    if not nullable:
        print("  No ε-productions found. Step skipped.")
        return g

    # --- add new productions for each combination of nullable omissions ---
    new_prods = {}
    for lhs, rules in g.productions.items():
        new_prods[lhs] = list(rules)  # copy existing

    for lhs, rhs in g.all_productions():
        if rhs == []:
            continue
        # positions of nullable symbols in this rhs
        nullable_positions = [i for i, s in enumerate(rhs) if s in nullable]
        # generate all non-empty subsets of those positions to omit
        for r in range(1, len(nullable_positions) + 1):
            for positions_to_omit in combinations(nullable_positions, r):
                new_rhs = [s for i, s in enumerate(rhs)
                           if i not in positions_to_omit]
                if new_rhs and new_rhs not in new_prods.get(lhs, []):
                    new_prods.setdefault(lhs, []).append(new_rhs)

    # --- remove all ε-productions (except start if nullable) ---
    for lhs in new_prods:
        new_prods[lhs] = [r for r in new_prods[lhs] if r != []]

    # If start is nullable, add S → ε back (language contains ε)
    if g.start in nullable:
        new_prods[g.start].append([])
        print(f"  Start symbol '{g.start}' is nullable → keeping S → ε")

    g.productions = new_prods
    return g


# ---------------------------------------------------------------------------
# Step 2 — Eliminate renaming (unit productions A → B)
# ---------------------------------------------------------------------------

def eliminate_renaming(grammar: Grammar) -> Grammar:
    """
    For each non-terminal A, compute the 'unit closure': all B reachable
    from A by chains of unit rules A→B→C→... . Then replace each unit
    chain with the non-unit productions of the final symbol.
    """
    g = grammar.copy()

    def unit_closure(start_sym):
        """Return all non-terminals reachable from start_sym via unit rules."""
        visited = {start_sym}
        queue = [start_sym]
        while queue:
            sym = queue.pop()
            for rhs in g.productions.get(sym, []):
                if len(rhs) == 1 and rhs[0] in g.nonterminals:
                    target = rhs[0]
                    if target not in visited:
                        visited.add(target)
                        queue.append(target)
        return visited

    new_prods = {lhs: [] for lhs in g.productions}
    for lhs in g.productions:
        closure = unit_closure(lhs)
        for sym in closure:
            for rhs in g.productions.get(sym, []):
                # Include only non-unit productions
                if not (len(rhs) == 1 and rhs[0] in g.nonterminals):
                    if rhs not in new_prods[lhs]:
                        new_prods[lhs].append(rhs)

    g.productions = new_prods
    return g


# ---------------------------------------------------------------------------
# Step 3 — Eliminate inaccessible symbols
# ---------------------------------------------------------------------------

def eliminate_inaccessible(grammar: Grammar) -> Grammar:
    """
    BFS/DFS from the start symbol: mark every non-terminal that appears
    in any reachable production RHS. Remove everything not reachable.
    """
    g = grammar.copy()

    reachable = {g.start}
    queue = [g.start]
    while queue:
        sym = queue.pop()
        for rhs in g.productions.get(sym, []):
            for s in rhs:
                if s in g.nonterminals and s not in reachable:
                    reachable.add(s)
                    queue.append(s)

    removed = g.nonterminals - reachable
    print(f"\n  Reachable non-terminals : {reachable}")
    print(f"  Inaccessible (removed)  : {removed if removed else '∅'}")

    g.nonterminals = reachable
    g.productions = {k: v for k, v in g.productions.items() if k in reachable}
    return g


# ---------------------------------------------------------------------------
# Step 4 — Eliminate non-productive symbols
# ---------------------------------------------------------------------------

def eliminate_nonproductive(grammar: Grammar) -> Grammar:
    """
    A non-terminal is productive if it can eventually derive a string of
    terminals. Start from terminals and work upward: a rule is productive
    if every symbol on its RHS is productive (terminals always are).
    """
    g = grammar.copy()

    productive = set(g.terminals)
    changed = True
    while changed:
        changed = False
        for lhs, rhs in g.all_productions():
            if lhs not in productive and all(s in productive for s in rhs):
                productive.add(lhs)
                changed = True

    nonproductive = g.nonterminals - (productive & g.nonterminals)
    print(f"\n  Productive symbols      : {productive & g.nonterminals}")
    print(f"  Non-productive (removed): {nonproductive if nonproductive else '∅'}")

    g.nonterminals = productive & g.nonterminals
    # Keep only productions where every symbol is productive
    new_prods = {}
    for lhs in g.nonterminals:
        rules = [rhs for rhs in g.productions.get(lhs, [])
                 if all(s in productive for s in rhs)]
        if rules:
            new_prods[lhs] = rules
    g.productions = new_prods
    return g


# ---------------------------------------------------------------------------
# Step 5 — Convert to Chomsky Normal Form
# ---------------------------------------------------------------------------

def to_cnf(grammar: Grammar) -> Grammar:
    """
    Two sub-steps:
    a) TERM: For every terminal 'a' appearing in a rule of length ≥ 2,
       introduce a new non-terminal T_a → a and replace 'a' with T_a.
    b) BIN:  For every rule with RHS length > 2, introduce new intermediate
       non-terminals to reduce it to binary.
    After this step every rule is either:
       A → BC   (two non-terminals)
       A → a    (single terminal)
    """
    g = grammar.copy()

    # --- TERM: replace terminals in long rules ---
    terminal_map = {}  # 'a' → 'T_a'
    new_prods_term = deepcopy(g.productions)

    for lhs, rules in g.productions.items():
        for idx, rhs in enumerate(rules):
            if len(rhs) >= 2:
                new_rhs = []
                for sym in rhs:
                    if sym in g.terminals:
                        if sym not in terminal_map:
                            name = fresh_name(g.nonterminals | set(terminal_map.values()),
                                              prefix=f"T{sym.upper()}")
                            terminal_map[sym] = name
                            g.nonterminals.add(name)
                        new_rhs.append(terminal_map[sym])
                    else:
                        new_rhs.append(sym)
                new_prods_term[lhs][idx] = new_rhs

    # Add the new terminal productions
    for term, nt in terminal_map.items():
        new_prods_term[nt] = [[term]]
        print(f"  TERM: introduced {nt} → {term}")

    g.productions = new_prods_term

    # --- BIN: break long rules into binary rules ---
    new_prods_bin = {}
    for lhs, rules in g.productions.items():
        new_prods_bin[lhs] = []
        for rhs in rules:
            if len(rhs) <= 2:
                new_prods_bin[lhs].append(rhs)
            else:
                # A → B1 B2 B3 ... Bn
                # becomes A → B1 N1, N1 → B2 N2, ..., N(n-2) → B(n-1) Bn
                current_lhs = lhs
                remaining = list(rhs)
                while len(remaining) > 2:
                    new_nt = fresh_name(g.nonterminals, prefix="BIN")
                    g.nonterminals.add(new_nt)
                    new_prods_bin.setdefault(current_lhs, []).append(
                        [remaining[0], new_nt]
                    )
                    # Remove the rule we just replaced if it was the original
                    if current_lhs != lhs:
                        pass  # already being built fresh
                    print(f"  BIN : {current_lhs} → {remaining[0]} {new_nt}  "
                          f"(split from {''.join(rhs)})")
                    remaining = remaining[1:]
                    current_lhs = new_nt

                new_prods_bin.setdefault(current_lhs, []).append(remaining)
                if len(remaining) == 2:
                    print(f"  BIN : {current_lhs} → {''.join(remaining)}  (tail)")

    g.productions = new_prods_bin
    return g


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def normalize_to_cnf(grammar: Grammar, verbose=True) -> Grammar:
    """
    Run all 5 normalization steps and return the CNF grammar.
    Prints a detailed trace of each step when verbose=True.
    """
    g = grammar

    steps = [
        ("Step 1: Eliminate ε-productions",    eliminate_epsilon),
        ("Step 2: Eliminate renaming",          eliminate_renaming),
        ("Step 3: Eliminate inaccessible symbols", eliminate_inaccessible),
        ("Step 4: Eliminate non-productive symbols", eliminate_nonproductive),
        ("Step 5: Convert to Chomsky Normal Form",  to_cnf),
    ]

    for title, fn in steps:
        if verbose:
            print(f"\n{'=' * 56}")
            print(f"  {title}")
            print(f"{'=' * 56}")
        g = fn(g)
        if verbose:
            g.print(f"After {title}")

    return g


# ---------------------------------------------------------------------------
# Verify CNF
# ---------------------------------------------------------------------------

def verify_cnf(grammar: Grammar) -> bool:
    """
    Check that every production is either A → BC or A → a.
    Returns True if the grammar is in CNF.
    """
    ok = True
    for lhs, rhs in grammar.all_productions():
        if len(rhs) == 1:
            if rhs[0] not in grammar.terminals:
                print(f"  [FAIL] {lhs} → {rhs[0]}  (single symbol but not terminal)")
                ok = False
        elif len(rhs) == 2:
            if not (rhs[0] in grammar.nonterminals and rhs[1] in grammar.nonterminals):
                print(f"  [FAIL] {lhs} → {''.join(rhs)}  (not two non-terminals)")
                ok = False
        else:
            print(f"  [FAIL] {lhs} → {''.join(rhs)}  (length {len(rhs)} > 2)")
            ok = False
    return ok


# ---------------------------------------------------------------------------
# Variant 12 grammar definition
# ---------------------------------------------------------------------------

VARIANT_12 = Grammar(
    start="S",
    terminals={"a", "b"},
    nonterminals={"S", "A", "B", "C", "D", "X"},
    productions={
        "S": [["A"]],
        "A": [["a", "X"], ["b", "X"]],
        "X": [[], ["B", "X"], ["b"]],
        "B": [["A", "D"]],
        "D": [["a", "D"], ["a"]],
        "C": [["C", "a"]],
    },
)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 56)
    print("  Lab 5 — Chomsky Normal Form  |  Variant 12")
    print("  Formal Languages & Finite Automata")
    print("=" * 56)

    VARIANT_12.print("Original Grammar (Variant 12)")

    cnf = normalize_to_cnf(VARIANT_12.copy())

    print(f"\n{'=' * 56}")
    print("  CNF Verification")
    print(f"{'=' * 56}")
    if verify_cnf(cnf):
        print("  All productions conform to CNF. ✓")
    else:
        print("  Some productions do NOT conform to CNF!")

    # --- Bonus: accept any grammar ---
    print(f"\n\n{'=' * 56}")
    print("  BONUS — Custom grammar input")
    print(f"{'=' * 56}")
    custom = Grammar(
        start="S",
        terminals={"a", "b", "c"},
        nonterminals={"S", "A", "B"},
        productions={
            "S": [["A", "B"], ["a"]],
            "A": [[], ["a", "A"], ["b"]],
            "B": [["b", "B"], ["S"], ["c"]],
        },
    )
    custom.print("Custom Grammar")
    cnf2 = normalize_to_cnf(custom.copy())
    print(f"\n{'=' * 56}")
    print("  CNF Verification (custom grammar)")
    print(f"{'=' * 56}")
    if verify_cnf(cnf2):
        print("  All productions conform to CNF. ✓")
    else:
        print("  Some productions do NOT conform to CNF!")


if __name__ == "__main__":
    main()