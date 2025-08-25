# 🚀 Quick Reference: Coverage Artifacts Access

## 🎯 What's New?

The CI/CD pipeline now automatically generates test coverage reports as downloadable artifacts! No more manual coverage generation - everything is automated.

## ⚡ Quick Access (2 minutes)

1. **Go to**: [GitHub Actions](https://github.com/aluiziorenato/ml_project/actions)
2. **Click**: Latest "ML Project CI/CD Pipeline" run
3. **Scroll down**: To "Artifacts" section  
4. **Download**: `coverage-reports-latest.zip`
5. **Extract & Open**: `backend-coverage-html/index.html`

## 📊 What You Get

- **Interactive HTML Reports** - Click through modules, see uncovered lines
- **XML Reports** - For IDE integration and tools
- **Coverage Badge** - For documentation
- **Automatic PR Comments** - Coverage summary on every pull request

## 🎯 Coverage Targets

| Module | Target | Current Status |
|--------|--------|----------------|
| `app/auth/` | 95% | ✅ Critical |
| `app/db/` | 90% | ✅ Critical |
| `app/routers/` | 85% | ⚠️ Important |
| `app/services/` | 80% | ⚠️ Important |
| **Overall** | **80%** | **🎯 Required** |

## 🔗 Key Links

- **📖 Full Documentation**: [Coverage Artifacts Guide](coverage-artifacts-guide.md)
- **📊 Codecov Dashboard**: https://codecov.io/gh/aluiziorenato/ml_project
- **🧪 Test Checklist**: [checklist_testes.md](../checklist_testes.md)

## 🆘 Need Help?

- Coverage not showing? Check workflow logs
- Can't download artifacts? Verify repository permissions
- Questions? Open a [GitHub Issue](https://github.com/aluiziorenato/ml_project/issues)

---
⏱️ **Total setup time**: < 2 minutes | 🔄 **Updates**: Automatic on every push/PR