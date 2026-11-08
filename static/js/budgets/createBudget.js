// ERYN + MICHALYN + MISHAYLE: Create Budget connected to Flask.
const budgetForm = document.getElementById('budgetForm');
const categorySelect = document.getElementById('category');
const monthlyAmount = document.getElementById('monthlyAmount');
const startDate = document.getElementById('startDate');
const endDate = document.getElementById('endDate');
const suggestionMessage = document.getElementById('suggestionMessage');
const suggestionResult = document.getElementById('suggestionResult');
const suggestedAmount = document.getElementById('suggestedAmount');
const useAmountBtn = document.getElementById('useAmountBtn');
const formMessage = document.getElementById('formMessage');
let currentRecommendation = null;
let recommendationRequestId = 0;
const formatRand = value => new Intl.NumberFormat('en-ZA', {style:'currency', currency:'ZAR'}).format(value);
function showFormError(message) { formMessage.textContent = message; formMessage.style.color = '#d62828'; }
function selectedPeriod() { return startDate.value ? startDate.value.slice(0,7) : new Date().toLocaleDateString('en-CA').slice(0,7); }
async function loadExpenseCategories() {
    try {
        const response = await fetch('/api/transaction-options', {credentials:'same-origin'});
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Could not load categories.');
        const categories = (data.categories || []).filter(c => String(c.category_type).toLowerCase() === 'expense');
        categories.forEach(c => {
            const option = document.createElement('option');
            option.value = c.category_id;
            option.textContent = c.category_name;
            categorySelect.appendChild(option);
        });
        if (!categories.length) showFormError('No expense categories are available.');
    } catch (error) { showFormError(error.message); }
}
async function updateSuggestedBudget() {
    const requestId = ++recommendationRequestId;
    const categoryId = categorySelect.value;
    const period = selectedPeriod();
    currentRecommendation = null;
    suggestionResult.hidden = true;
    if (!categoryId) { suggestionMessage.textContent = 'Select a category to view your suggested budget.'; return; }
    suggestionMessage.textContent = 'Calculating suggested budget...';
    try {
        const params = new URLSearchParams({category_id: categoryId, period});
        const response = await fetch('/api/budgets/recommendation?' + params, {credentials:'same-origin'});
        const data = await response.json();
        if (requestId !== recommendationRequestId || categorySelect.value !== categoryId || selectedPeriod() !== period) return;
        if (!response.ok) throw new Error(data.error || 'Unable to calculate a suggestion.');
        const amount = data.suggested_amount;
        if (amount === null || amount === undefined || !Number.isFinite(Number(amount))) {
            suggestionMessage.textContent = data.message || 'Insufficient spending history to suggest a budget.';
            return;
        }
        currentRecommendation = Number(amount);
        suggestedAmount.textContent = formatRand(currentRecommendation);
        suggestionMessage.textContent = data.message || 'Based on your previous spending.';
        suggestionResult.hidden = false;
    } catch (error) {
        if (requestId !== recommendationRequestId) return;
        suggestionMessage.textContent = error.message;
    }
}
categorySelect.addEventListener('change', () => {formMessage.textContent=''; updateSuggestedBudget();});
startDate.addEventListener('change', () => {
    endDate.min = startDate.value;
    if (endDate.value && endDate.value < startDate.value) endDate.value='';
    formMessage.textContent='';
    updateSuggestedBudget();
});
endDate.addEventListener('change', () => {formMessage.textContent='';});
monthlyAmount.addEventListener('input', () => {formMessage.textContent='';});
useAmountBtn.addEventListener('click', () => {
    if (currentRecommendation === null) return;
    monthlyAmount.value = currentRecommendation;
    monthlyAmount.focus();
    formMessage.textContent='Suggested amount applied. You can still change it.';
    formMessage.style.color='#1558e8';
});
budgetForm.addEventListener('submit', async event => {
    event.preventDefault();
    const amount = Number(monthlyAmount.value);
    if (!categorySelect.value) return showFormError('Please select a category.');
    if (!Number.isFinite(amount) || amount <= 0) return showFormError('Please enter a valid monthly amount.');
    if (!startDate.value || !endDate.value || endDate.value < startDate.value) return showFormError('Please select a valid date range.');
    const saveButton = document.getElementById('saveBudgetBtn');
    saveButton.disabled = true;
    formMessage.textContent='Saving budget...';
    try {
        const response = await fetch('/api/budgets', {
            method:'POST', credentials:'same-origin', headers:{'Content-Type':'application/json'},
            body:JSON.stringify({category_id:Number(categorySelect.value), budget_amount:amount, start_date:startDate.value, end_date:endDate.value})
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Could not save budget.');
        window.location.assign('/budgets?period=' + encodeURIComponent(startDate.value.slice(0,7)));
    } catch (error) { showFormError(error.message); saveButton.disabled=false; }
});
loadExpenseCategories();
