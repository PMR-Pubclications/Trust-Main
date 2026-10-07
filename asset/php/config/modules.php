<?php
/**
 * TRUST-SHELL CAPABILITIES & MODULE REGISTRY
 * To add a new capability, simply add a new array block below.
 */
return [
    // ----------------------------------------------------
    // SYSTEM NAVIGATION CAPABILITIES
    // ----------------------------------------------------
    [
        'id'          => 'duty_roster',
        'title'       => 'Duty Roster',
        'icon'        => '&#128100;',
        'url'         => 'index.php',
        'category'    => 'system',
        'allowed_roles' => ['trust_admin', 'first_responder', 'responder', 'standard']
    ],
    [
        'id'          => 'guide',
        'title'       => "User's Guide",
        'icon'        => '&#128216;',
        'url'         => 'guide.php',
        'category'    => 'system',
        'allowed_roles' => ['trust_admin', 'first_responder', 'responder']
    ],
    [
        'id'          => 'app_status',
        'title'       => 'App Behavior & Health',
        'icon'        => '&#128187;',
        'url'         => 'app_status.php',
        'category'    => 'system',
        'allowed_roles' => ['trust_admin'] // Trust Admin Only
    ],
    [
        'id'          => 'payroll',
        'title'       => 'Payroll Maintenance',
        'icon'        => '&#128178;',
        'url'         => 'payroll.php',
        'category'    => 'system',
        'allowed_roles' => ['trust_admin'] // Trust Admin Only
    ],
    [
        'id'          => 'admin_onboarding',
        'title'       => 'Admin Onboarding',
        'icon'        => '&#128221;',
        'url'         => 'onboarding.php',
        'category'    => 'system',
        'allowed_roles' => ['trust_admin']
    ],
    [
        'id'          => 'responder_onboarding',
        'title'       => 'Responder Onboarding',
        'icon'        => '&#128657;',
        'url'         => 'responder_onboarding.php',
        'category'    => 'system',
        'allowed_roles' => ['first_responder', 'responder']
    ],

    // ----------------------------------------------------
    // EXAMPLE: FUTURE CAPABILITY (Just uncomment to activate!)
    // ----------------------------------------------------
    /*
    [
        'id'          => 'incident_logs',
        'title'       => 'Live Incident Dispatch',
        'icon'        => '&#128680;',
        'url'         => 'dispatch.php',
        'category'    => 'system',
        'allowed_roles' => ['trust_admin', 'first_responder']
    ],
    */
];
