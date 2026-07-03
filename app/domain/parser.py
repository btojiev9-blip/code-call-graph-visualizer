import ast

# 1. Test code with English strings
test_code = """
def process_order():
    check_stock()
    get_payment()

def check_stock():
    print("Stock is OK")

def get_payment():
    check_credit_card()

def check_credit_card():
    print("Card is OK")
"""

# 2. Graph builder class
class GraphBuilder(ast.NodeVisitor):
    def __init__(self):
        self.current_function = None
        self.links = []

    def visit_FunctionDef(self, node):
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and self.current_function:
            called_function = node.func.id
            if called_function != "print":
                self.links.append(f"{self.current_function} --> {called_function}")
        self.generic_visit(node)


# 3. Main function for API
def analyze_code_to_mermaid(code_text: str) -> str:
    try:
        tree = ast.parse(code_text)
        builder = GraphBuilder()
        builder.visit(tree)
        
        mermaid_template = "graph TD\n"
        for link in builder.links:
            mermaid_template += f"    {link}\n"
            
        return mermaid_template
    except Exception as e:
        return f"Error: {str(e)}"


# 4. Local launch trigger
if __name__ == "__main__":
    print("--- RUNNING LOCAL TEST ---")
    result = analyze_code_to_mermaid(test_code)
    print(result)