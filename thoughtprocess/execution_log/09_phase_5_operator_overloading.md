# Execution Log: Overloading CloudNode Dunder Methods

## Explanation
The user experience of the `diagrams` library relies entirely on Python operator overloading. Specifically, the bitwise shift operators:
*   `NodeA >> NodeB` translates to `A connects to B`
*   `NodeA << NodeB` translates to `B connects to A`
*   `NodeA - NodeB` translates to `A connects to B AND B connects to A`

To intercept this syntax in `manim-devops`, we must add the `__rshift__`, `__lshift__`, and `__sub__` dunder methods directly to our base `CloudNode` class.

---

## The 3 Why's (Validating the Test Necessity)

1. **Why put these methods on the base abstract `CloudNode`?**
   Because every valid Manim object we create (like `EC2` or `RDS`) inherits from `CloudNode`. Putting the overloads on the base class instantly applies the `diagrams` syntax to our entire asset library without code duplication.
2. **How does the overloaded method know about the Topology?**
   The overloads will import the `adapter._ACTIVE_DIAGRAM` global variable we built in the previous step. If a diagram is active, the operation will call `add_node()` and `connect()` on that underlying `Topology` instance automatically.
3. **What if the user writes `A >> B` but forgot the `with AnimatedDiagram():` block?**
   We must fail fast. The dunder method must raise a `RuntimeError` explicitely stating that layout nodes must be instantiated within a valid Context Manager. This prevents silent execution failures.

---

## 3 Deep Technical Questions (The `__rshift__` Implementation)

1. **Chaining Syntax:** The `diagrams` library supports chaining, like `A >> B >> C`. How does this work? 
   *Answer:* The `__rshift__` method must return `self` or the `target` node, depending on the flow. Actually, for `A >> B >> C`, `A>>B` evaluates first, returning `B`. Then `B>>C` evaluates next. Therefore, the method MUST return the right-side operand (`target` node).
2. **List Evaluation:** The diagrams library allows mapping a node to a list `A >> [B, C]`. Do we need to support list unrolling?
   *Answer:* Yes. The dunder method must use `isinstance(target, list)` and iterate over the targets to connect `self` to each item in the list, then return the list.
3. **Import Cycles:** If `CloudNode` imports `adapter._ACTIVE_DIAGRAM` at the top of the file, and `adapter` imports `Topology`, which imports `CloudNode`... do we risk a circular import?
   *Answer:* Yes. We must defer the import of `_ACTIVE_DIAGRAM` until *inside* the executing `__rshift__` method to prevent circular reference lockouts.

---

## Self-Reflection & Execution Blueprint
The requirement for "List Support" (Question 2) is a massive API surface multiplier. If `[A, B] >> C` is valid, then we can't just put Dunders on `CloudNode`. Python's native `list` doesn't support `>>` targeting a `CloudNode`. 
However, for the MVP Phase 5 adapter, we will explicitly restrict our adapter to Single-Node shifts (`A >> B`, or `A >> [B, C]`) since overloading the native Python `.list()` object requires rewriting a custom NodeGroup wrapper. We will start strictly with `CloudNode >> CloudNode` and verify list extensions later.

**The Red Phase Strategy:**
Write a Pytest that instantiates an `AnimatedDiagram`, uses the `a >> b >> c` syntax, and asserts that the `Topology` math engine recorded the edges correctly. Write a second test asserting a `RuntimeError` if used outside the context.
