// MICHALYN: Budget dashboard table, month selector, progress bars.
// MISHAYLE: Connected to Daniel's saved budgets and transaction spending.
let selectedBudgetMonth = window.finSyncInitialBudgetPeriod || new Date().toLocaleDateString('en-CA').slice(0,7);
function budgetMoney(amount) { return 'R ' + Number(amount).toLocaleString('en-ZA',{minimumFractionDigits:2,maximumFractionDigits:2}); }
function showBudgets(container) {
    container.innerHTML = `<div class="budget-actions"><label for="budget-month">Budget month</label>
    <input id="budget-month" type="month" aria-label="Budget month">
    <button type="button" id="add-budget-btn">+ Add Budget</button></div>
    <div class="budget-table-wrap"><table class="budget-table" aria-label="Monthly budgets">
    <thead><tr><th>Category</th><th>Spent</th><th>Budget</th><th>Progress</th></tr></thead>
    <tbody id="budget-rows"></tbody></table></div><p id="budget-status" role="status"></p>`;
    const month = document.getElementById('budget-month');
    month.value = selectedBudgetMonth;
    month.addEventListener('change', () => {selectedBudgetMonth=month.value; loadBudgetRows();});
    document.getElementById('add-budget-btn').addEventListener('click', () => {window.location.href='/budgets/create';});
    loadBudgetRows();
}
let budgetLoadId=0;
async function loadBudgetRows() {
    const requestId=++budgetLoadId;
    const body=document.getElementById('budget-rows');
    const status=document.getElementById('budget-status');
    body.replaceChildren(); status.textContent='Loading budgets...';
    try {
        const response=await fetch('/api/budgets?period='+encodeURIComponent(selectedBudgetMonth),{credentials:'same-origin'});
        const data=await response.json();
        if(requestId!==budgetLoadId) return;
        if(!response.ok) throw new Error(data.error||'Unable to load budgets.');
        status.textContent='';
        (data.budgets||[]).forEach(record => {
            const percent=record.budget>0?Math.round(record.spent/record.budget*100):0;
            const row=document.createElement('tr');
            [record.category,budgetMoney(record.spent),budgetMoney(record.budget)].forEach(value=>{
                const cell=document.createElement('td');cell.textContent=value;row.appendChild(cell);
            });
            const cell=document.createElement('td');
            const progress=document.createElement('div');progress.className='budget-progress';
            const track=document.createElement('div');track.className='budget-track';
            track.setAttribute('role','progressbar');track.setAttribute('aria-label',record.category+' budget used');
            track.setAttribute('aria-valuemin','0');track.setAttribute('aria-valuemax','100');
            track.setAttribute('aria-valuenow',Math.min(percent,100));
            track.setAttribute('aria-valuetext',percent+'% spent');
            const fill=document.createElement('div');fill.className='budget-fill'+(percent>=90?' budget-warning':'');
            fill.style.width=Math.max(0,Math.min(percent,100))+'%';track.appendChild(fill);
            const label=document.createElement('span');label.textContent=percent+'%';
            progress.append(track,label);cell.appendChild(progress);row.appendChild(cell);body.appendChild(row);
        });
        if(!(data.budgets||[]).length){const row=document.createElement('tr');const cell=document.createElement('td');cell.colSpan=4;cell.className='budget-empty';cell.textContent='No budgets recorded for this month.';row.appendChild(cell);body.appendChild(row);}
    } catch(error){if(requestId===budgetLoadId)status.textContent=error.message;}
}

document.querySelectorAll(".nav-btn").forEach(function(button) {

    button.classList.toggle(
        "active",
        button.dataset.page === "Budgets"
    );

    button.addEventListener("click", function() {

        if (button.dataset.page === "Dashboard") {
            window.location.href = "/dashboard";
            return;
        }

        if (button.dataset.page === "Transactions") {
            window.location.href = "/transactions";
            return;
        }

        // MISHAYLE: Open Savings Goals
        if (button.dataset.page === "Savings Goals") {
            window.location.href = "/savings-goals";
            return;
        }

        // MISHAYLE: Open the Reports page
        if (button.dataset.page === "Reports") {
            window.location.href = "/reports";
            return;
        }

        if (button.dataset.page === "Settings") {
            window.location.href = "/settings";

        }

        // Other pages are not implemented yet.
    });
});

document.getElementById('logout-btn').addEventListener('click',()=>{window.location.href=window.finSyncLogoutUrl;});
showBudgets(document.getElementById('page-content'));
