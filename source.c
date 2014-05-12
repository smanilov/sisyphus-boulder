void f() {
}

int main() {
        for (int j = 0; j < m; ++j) {
                f();
                for (int i = 0; i < n; ++i) {
                        f();
                        for (int k = 0; k < n; ++k) {
                                f();
                        }
                        f();
                }
                f();
                for (int i = 0; i < n; ++i) {
                        f();
                }
                f();
        }
}
