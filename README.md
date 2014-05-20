Sisyphus Boulder
================

Automatic loop unroller
-----------------------

Ever needed a quick and dirty way to unroll a loop?

Before:

```
void f(int j) {
}

int main() {
        for (int j = 0; j < m; ++j) {
                f(j);
        }
}
```

After:

```
void f(int j) {
}

int main() {
        for (int j = 0; j < m; j += 4) {
                f(j + 0);
                f(j + 1);
                f(j + 2);
                f(j + 3);
        }
}
```

This is what Sisyphus Boulder is about.
