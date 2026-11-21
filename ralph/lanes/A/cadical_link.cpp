#include <cstdio>
#include <vector>
#include "cadical.hpp"

class Observer : public CaDiCaL::ExternalPropagator {
public:
    bool checked = false;
    void notify_assignment(const std::vector<int> &) override {}
    void notify_new_decision_level() override {}
    void notify_backtrack(std::size_t) override {}
    bool cb_check_found_model(const std::vector<int> &model) override {
        for (int literal : model) if (literal == 1) checked = true;
        return true;
    }
    bool cb_has_external_clause(bool &) override { return false; }
    int cb_add_external_clause_lit() override { return 0; }
};

int main() {
    Observer observer;
    CaDiCaL::Solver solver;
    solver.connect_external_propagator(&observer);
    solver.add_observed_var(1);
    solver.add(1);
    solver.add(0);
    const int result = solver.solve();
    solver.disconnect_external_propagator();
    if (result != 10 || !observer.checked || solver.val(1) != 1) return 1;
    std::puts("IPASIR-UP OK");
}
