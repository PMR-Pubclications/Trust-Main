/**
 * Automated Payroll & Deduction Engine
 * Calculates gross pay, federal FICA, and Washington State mandatory withholdings.
 */

const fs = require('fs');

function calculatePay() {
    // 1. Load configuration and active time cards
    const payScale = JSON.parse(fs.readFileSync('./pay-scale.json', 'utf8'));
    const timecard = JSON.parse(fs.readFileSync('./timecards/active-log.json', 'utf8'));

    // 2. Find matching role details
    const role = payScale.roles.find(r => r.role_id === timecard.role_id);
    if (!role) {
        console.error(`[ERROR] Role ID ${timecard.role_id} not found in pay scale.`);
        process.exit(1);
    }

    // 3. Compute Gross Pay
    const regularPay = timecard.regular_hours * role.base_hourly_rate;
    const overtimePay = timecard.overtime_hours * (role.base_hourly_rate * role.overtime_multiplier);
    const grossPay = regularPay + overtimePay;

    // 4. Compute Mandatory Deductions (2026 Federal & WA Standards)
    // Social Security (6.2% up to $184,500 wage cap)
    const socialSecurity = grossPay * 0.062;

    // Medicare (1.45% on all earnings)
    const medicare = grossPay * 0.0145;

    // WA Paid Family & Medical Leave (Employee share approx 0.806% of total 1.13% premium)
    const waPFML = grossPay * 0.00806;

    // WA Cares Fund (Long-term care: 0.58%)
    const waCares = grossPay * 0.0058;

    const totalDeductions = socialSecurity + medicare + waPFML + waCares;
    const netPay = grossPay - totalDeductions;

    // 5. Output Summary Report
    const report = {
        employee: timecard.employee_name,
        period_station: timecard.console_station_id,
        gross_pay: Number(grossPay.toFixed(2)),
        deductions: {
            social_security: Number(socialSecurity.toFixed(2)),
            medicare: Number(medicare.toFixed(2)),
            wa_pfml: Number(waPFML.run ? waPFML.toFixed(2) : waPFML.toFixed(2)),
            wa_cares_fund: Number(waCares.toFixed(2)),
            total_deductions: Number(totalDeductions.toFixed(2))
        },
        net_pay: Number(netPay.toFixed(2)),
        timestamp: new Date().toISOString()
    };

    console.log("--- AUTOMATED PAYROLL CALCULATION ---");
    console.log(JSON.stringify(report, null, 2));
}

calculatePay();
