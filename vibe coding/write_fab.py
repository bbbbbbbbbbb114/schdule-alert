# write_fab.py
with open('app/static/css/styles.css', 'a', encoding='utf-8') as f:
    f.write('''

/* ====================================================
   FAB BUTTON (Floating Action Button)
==================================================== */
.btn-fab {
    position: fixed;
    bottom: 32px;
    right: 32px;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: var(--primary);
    color: white;
    font-size: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    cursor: pointer;
    z-index: 1000;
    box-shadow: 0 0 0 0 rgba(221, 91, 0, 0.4), var(--shadow-deep);
    transition: all 0.3s var(--ease-spring);
}
.btn-fab:hover {
    transform: translateY(-4px) scale(1.05);
    box-shadow: 0 0 0 6px rgba(221, 91, 0, 0), var(--shadow-deep);
}
''')
