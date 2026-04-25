"""
pid_plots.py — all matplotlib visualization for the Never Crash PID tutorial.

Each function receives pre-computed simulation data (or other parameters) and
produces one figure. Keep plotting details here so the notebook stays focused
on PID concepts.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

plt.rcParams.update({
    'figure.figsize'   : [13, 5],
    'font.size'        : 11,
    'axes.grid'        : True,
    'grid.alpha'       : 0.3,
    'axes.spines.top'  : False,
    'axes.spines.right': False,
    'lines.linewidth'  : 2.2,
})

C_P      = '#FF8C00'   # orange       — Proportional
C_I      = '#2196F3'   # blue         — Integral
C_D      = '#9C27B0'   # purple       — Derivative
C_PID    = '#2E7D32'   # dark green   — full PID
C_target = '#2E7D32'   # same green   — target line
C_dist   = '#1565C0'   # dark blue    — distance trace
C_err    = '#E53935'   # red          — error


# ── Part 1 ────────────────────────────────────────────────────────────────────

def plot_naive_strategies(target):
    """Open-loop vs bang-bang — show why both fail."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    t = np.linspace(0, 5, 200)

    for speed, color, lbl in [
        (4,  '#90CAF9', 'Slow (4 cm/s)'),
        (10, '#FF9800', 'Medium (10 cm/s)'),
        (20, '#F44336', 'Fast (20 cm/s)'),
    ]:
        axes[0].plot(t, np.maximum(30 - speed * t, 0), color=color, label=lbl)

    axes[0].axhline(target, color=C_target, linestyle='--', lw=2,
                    label=f'Target ({target} cm)')
    axes[0].fill_between([0, 5], [-1, -1], [0, 0], color='gray', alpha=0.4)
    axes[0].text(2.5, -0.7, '🧱 WALL', ha='center', fontsize=9, fontweight='bold')
    axes[0].set(xlim=[0, 5], ylim=[-1.5, 33], xlabel='Time (s)', ylabel='Distance (cm)',
                title='Open Loop — constant throttle\n"Just drive and hope for the best"')
    axes[0].legend(fontsize=9)

    dist_bb, dists_bb = 30.0, [30.0]
    for _ in range(199):
        spd = 14 if dist_bb > target else -14
        dist_bb = max(0, dist_bb - spd * 0.025)
        dists_bb.append(dist_bb)

    axes[1].plot(t, dists_bb, color='#9C27B0', lw=2)
    axes[1].axhline(target, color=C_target, linestyle='--', lw=2,
                    label=f'Target ({target} cm)')
    axes[1].set(xlim=[0, 5], ylim=[-1.5, 33], xlabel='Time (s)', ylabel='Distance (cm)',
                title='Bang-Bang — full gas or full brake\n"React as hard as possible"')
    axes[1].legend()

    plt.suptitle('Neither strategy works well — we need something smarter',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.show()


# ── Part 2 ────────────────────────────────────────────────────────────────────

def plot_error_signal(data, target):
    """Distance and error signal side-by-side."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 6), sharex=True)

    ax1.plot(data['time'], data['distance'], color=C_dist, label='Actual distance')
    ax1.axhline(target, color=C_target, linestyle='--', lw=2,
                label=f'Target = {target} cm')
    ax1.fill_between(data['time'], data['distance'], target,
                     where=data['distance'] > target, alpha=0.15,
                     color='orange', label='Too far (error > 0)')
    ax1.fill_between(data['time'], data['distance'], target,
                     where=data['distance'] < target, alpha=0.15,
                     color='red', label='Too close (error < 0)')
    ax1.set(ylabel='Distance (cm)', title='Car Distance vs Target', ylim=[0, 35])
    ax1.legend(loc='upper right', fontsize=9)

    idx = 30
    ax1.annotate(
        f'error = {data["distance"][idx]:.1f} − {target} = {data["error"][idx]:.1f} cm',
        xy=(data['time'][idx], data['distance'][idx]),
        xytext=(data['time'][idx] + 1.5, data['distance'][idx] + 5),
        arrowprops=dict(arrowstyle='->', color='black'), fontsize=10,
    )

    ax2.plot(data['time'], data['error'], color=C_err,
             label='error = distance − target')
    ax2.axhline(0, color=C_target, linestyle='--', lw=2,
                label='error = 0  (perfect!)')
    ax2.fill_between(data['time'], data['error'], 0,
                     where=data['error'] > 0, alpha=0.2, color='orange')
    ax2.fill_between(data['time'], data['error'], 0,
                     where=data['error'] < 0, alpha=0.2, color='red')
    ax2.set(xlabel='Time (seconds)', ylabel='Error (cm)',
            title='Error = Distance − Target')
    ax2.legend()

    plt.tight_layout()
    plt.show()


# ── Part 3 ────────────────────────────────────────────────────────────────────

def plot_kp_comparison(datasets, target):
    """Three Kp values side-by-side. datasets: list of (data, color, title)."""
    fig, axes = plt.subplots(1, len(datasets), figsize=(15, 4.5), sharey=True)

    for ax, (data, color, title) in zip(axes, datasets):
        ax.plot(data['time'], data['distance'], color=color, lw=2.5)
        ax.axhline(target, color=C_target, linestyle='--', lw=2)
        ax.fill_between(data['time'], target - 1, target + 1,
                        alpha=0.1, color='green', label='±1 cm window')
        ax.set(xlabel='Time (s)', title=title, ylim=[0, 35])

        settled = np.where(np.abs(data['error']) < 1.0)[0]
        if len(settled):
            ts = data['time'][settled[0]]
            ax.axvline(ts, color=color, linestyle=':', alpha=0.8)
            ax.text(ts + 0.2, 27, f'settles\n~{ts:.0f}s', color=color, fontsize=9)

    axes[0].set_ylabel('Distance (cm)')
    plt.suptitle('P-Only Control:   throttle = Kp × (distance − target)',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.show()


def plot_kp_tune(data, kp_value, target):
    """Single Kp run with distance and throttle panels."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 6), sharex=True)

    ax1.plot(data['time'], data['distance'], color=C_P, lw=2.5)
    ax1.axhline(target, color=C_target, linestyle='--', lw=2)
    ax1.fill_between(data['time'], target - 1, target + 1, alpha=0.12, color='green')
    ax1.set(ylabel='Distance (cm)', title=f'P-Only  Kp={kp_value}', ylim=[0, 35])

    ax2.plot(data['time'], data['throttle'], color='steelblue', lw=2)
    ax2.axhline(0, color='k', lw=0.8)
    ax2.set(xlabel='Time (s)', ylabel='Throttle', ylim=[-1.2, 1.2])

    plt.tight_layout()
    plt.show()

    settled = np.where(np.abs(data['error']) < 0.5)[0]
    settle_str = (f'{data["time"][settled[0]]:.1f}s'
                  if len(settled) else 'never (within run)')
    print(f'Kp={kp_value}  |  Settles within 0.5 cm at: {settle_str}')
    print(f'Final error: {data["error"][-1]:.2f} cm')


# ── Part 4 ────────────────────────────────────────────────────────────────────

def plot_steady_state_error(data_p, target, kp, disturbance):
    """P-only steady-state error with math explanation."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

    ss_dist = np.mean(data_p['distance'][-60:])
    ss_err  = ss_dist - target

    axes[0].plot(data_p['time'], data_p['distance'], color=C_P, lw=2.5,
                 label='P-only + disturbance')
    axes[0].axhline(target,  color=C_target, linestyle='--', lw=2,
                    label=f'Target ({target} cm)')
    axes[0].axhline(ss_dist, color=C_err, linestyle=':', lw=2,
                    label=f'Settles at {ss_dist:.1f} cm (error = {ss_err:.1f} cm)')
    axes[0].fill_between(data_p['time'], target, ss_dist, alpha=0.15, color='red')
    axes[0].set(xlabel='Time (s)', ylabel='Distance (cm)',
                title='P-Only with disturbance\n(steady-state error — never reaches target)',
                ylim=[5, 35])
    axes[0].legend(fontsize=9)

    axes[1].axis('off')
    txt = (
        'Why does this happen?\n\n'
        'The car settles when throttle\n'
        'exactly balances the disturbance:\n\n'
        '   P = disturbance_force\n'
        '   Kp x error_ss = disturbance\n\n'
        f'   {kp} x error_ss = {disturbance}\n'
        f'   error_ss = {disturbance / kp:.2f} cm\n\n'
        f'Car stops at {target} + {disturbance/kp:.2f} = {target + disturbance/kp:.2f} cm\n\n'
        'To fix this, we need a term\n'
        'that KEEPS PUSHING even when\n'
        'the error is small but persistent.\n\n'
        '->  Enter: the Integral term'
    )
    axes[1].text(0.1, 0.95, txt, transform=axes[1].transAxes,
                 va='top', fontsize=11, fontfamily='monospace',
                 bbox=dict(boxstyle='round', facecolor='#FFF9C4', alpha=0.8))
    axes[1].set_title('The Math Behind Steady-State Error', fontsize=11)

    plt.suptitle('P Alone Cannot Eliminate a Constant Disturbance',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.show()


# ── Part 5 ────────────────────────────────────────────────────────────────────

def plot_integral_detail(data, target, ki_demo=0.015):
    """Four-panel breakdown of how the integral accumulates."""
    t, err = data['time'], data['error']

    fig = plt.figure(figsize=(13, 9))
    gs  = GridSpec(3, 2, figure=fig, hspace=0.55, wspace=0.35)
    ax_dist = fig.add_subplot(gs[0, :])
    ax_err  = fig.add_subplot(gs[1, :])
    ax_int  = fig.add_subplot(gs[2, 0])
    ax_txt  = fig.add_subplot(gs[2, 1])

    ss = np.mean(data['distance'][-60:])
    ax_dist.plot(t, data['distance'], color=C_dist, lw=2.5)
    ax_dist.axhline(target, color=C_target, linestyle='--', lw=2, label='Target')
    ax_dist.axhline(ss, color=C_err, linestyle=':', lw=2,
                    label=f'Settles at {ss:.1f} cm')
    ax_dist.fill_between(t, target, data['distance'],
                         where=data['distance'] > target, alpha=0.15, color='red')
    ax_dist.set(ylabel='Distance (cm)',
                title='P-Only with Disturbance: Persistent error', ylim=[5, 35])
    ax_dist.legend(fontsize=9)

    ax_err.plot(t, err, color=C_err, lw=2.5)
    ax_err.fill_between(t, 0, err, where=err >= 0, alpha=0.30, color='orange',
                        label='Accumulated area = integral')
    ax_err.fill_between(t, 0, err, where=err < 0, alpha=0.30, color='steelblue',
                        label='Negative area (subtracts)')
    ax_err.axhline(0, color=C_target, linestyle='--', lw=2)
    idx = 120
    ax_err.axvspan(t[idx], t[idx] + 0.1, alpha=0.7, color='red', zorder=5)
    ax_err.annotate(
        f'Slice = error × dt\n= {err[idx]:.2f} × 0.05',
        xy=(t[idx] + 0.05, err[idx] / 2),
        xytext=(t[idx] + 2.5, err[idx] + 1.5),
        arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
        fontsize=9, color='red',
    )
    ax_err.set(ylabel='Error (cm)',
               title='Error over time — shaded area = integral accumulating')
    ax_err.legend(fontsize=9)

    integral_vals = np.cumsum(err) * 0.05
    ax_int.plot(t, integral_vals, color=C_I, lw=2.5)
    ax_int.fill_between(t, 0, integral_vals, alpha=0.2, color=C_I)
    ax_int.set(xlabel='Time (s)', ylabel='Integral (cm·s)',
               title='Integral value keeps growing\nwhile error persists')

    ax_txt.axis('off')
    final_int = integral_vals[-1]
    explanation = (
        'After the car settles:\n\n'
        f'  Error ~ {np.mean(err[-60:]):.2f} cm  (small but persistent)\n'
        f'  Integral ~ {final_int:.1f} cm*s  (LARGE from accumulating)\n\n'
        f'  I = Ki x integral\n'
        f'  I = {ki_demo} x {final_int:.0f} = {ki_demo * final_int:.2f}\n\n'
        'This extra throttle overcomes\n'
        'the disturbance, driving error\n'
        'all the way to zero.\n\n'
        '"I have been off-target for a\n'
        'long time - I need to push harder."'
    )
    ax_txt.text(0.05, 0.95, explanation, transform=ax_txt.transAxes,
                va='top', fontsize=10, fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='#E3F2FD', alpha=0.9))
    ax_txt.set_title('Why the Integral Wins', fontsize=11)

    plt.suptitle('THE INTEGRAL: Accumulated Error Over Time  (area under the curve)',
                 fontsize=13, fontweight='bold')
    plt.show()


def plot_pi_comparison(data_p, data_pi, target):
    """P-only vs PI side-by-side with disturbance."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)

    pairs = [
        (axes[0], data_p,  C_P, 'P-Only  (Kp=0.08, Ki=0)\nStuck with steady-state error'),
        (axes[1], data_pi, C_I, 'PI Control  (Kp=0.08, Ki=0.015)\nFinds the target!'),
    ]
    for ax, data, color, title in pairs:
        ax.plot(data['time'], data['distance'], color=color, lw=2.5)
        ax.axhline(target, color=C_target, linestyle='--', lw=2,
                   label=f'Target {target} cm')
        ax.fill_between(data['time'], target - 0.5, target + 0.5,
                        alpha=0.15, color='green', label='±0.5 cm window')
        final = abs(data['error'][-1])
        ax.set(xlabel='Time (s)', title=title, ylim=[4, 35])
        ax.text(0.02, 0.06, f'Final error: {final:.2f} cm',
                transform=ax.transAxes, fontsize=10,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.85))
        ax.legend(fontsize=9)

    axes[0].set_ylabel('Distance (cm)')
    plt.suptitle('Adding Integral (I) Eliminates Steady-State Error',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.show()


# ── Part 6 ────────────────────────────────────────────────────────────────────

def plot_derivative_concept():
    """Slope tangents on a rich error curve + derivative panel."""
    t   = np.linspace(0, 6, 600)
    dt  = t[1] - t[0]
    err = 18 * np.exp(-0.45 * t) * np.cos(2.2 * t + 0.4)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 7), sharex=True)

    ax1.plot(t, err, color=C_dist, lw=2.5, label='Error over time', zorder=5)
    ax1.axhline(0, color=C_target, linestyle='--', lw=2,
                label='Error = 0  (perfect!)')
    ax1.set(ylabel='Error (cm)', title='Derivative = Slope at Each Moment')

    moments = [
        (0.25, '#E53935', 'Falling steeply\n(approaching fast)\nD brakes hard'),
        (1.45, '#FF9800', 'Near zero crossing\n(error small, changing fast)'),
        (2.50, '#9C27B0', 'Rising steeply\n(moving away fast)\nD pushes back'),
        (4.10, '#4CAF50', 'Nearly flat\n(almost settled)\nD ≈ 0'),
    ]
    for t_c, color, label in moments:
        idx   = max(1, min(int(t_c / dt), len(t) - 2))
        slope = (err[min(idx + 1, len(err) - 1)] - err[max(idx - 1, 0)]) / (2 * dt)
        t_tang = np.array([t_c - 0.55, t_c + 0.55])
        e_tang = err[idx] + slope * (t_tang - t_c)
        ax1.plot(t_tang, e_tang, color=color, lw=2, linestyle='--', alpha=0.9)
        ax1.plot(t_c, err[idx], 'o', color=color, ms=11, zorder=10)
        ax1.annotate(
            f'slope={slope:.1f}\n{label}',
            xy=(t_c, err[idx]),
            xytext=(t_c + 0.35, err[idx] + (5 if err[idx] < 0 else -5)),
            fontsize=8, color=color,
            arrowprops=dict(arrowstyle='->', color=color, lw=1.2),
        )
    ax1.legend(fontsize=9)

    deriv = np.gradient(err, t)
    ax2.plot(t, deriv, color=C_D, lw=2.5, label='Derivative (slope of error)')
    ax2.fill_between(t, 0, deriv, where=deriv < 0, alpha=0.2, color=C_I,
                     label='Negative: error falling (approaching)')
    ax2.fill_between(t, 0, deriv, where=deriv > 0, alpha=0.2, color=C_err,
                     label='Positive: error rising (moving away)')
    ax2.axhline(0, color=C_target, linestyle='--', lw=2)
    ax2.set(xlabel='Time (s)', ylabel='d(error)/dt  (cm/s)',
            title='Derivative Term — D = Kd × derivative')
    ax2.legend(fontsize=9)

    plt.tight_layout()
    plt.show()


def plot_pd_comparison(data_p, data_pd, target):
    """P-only vs PD — oscillation damping."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)

    pairs = [
        (axes[0], data_p,  C_P, 'P-Only  (Kp=0.25, Kd=0)\nOscillates — keeps overshooting'),
        (axes[1], data_pd, C_D, 'PD Control  (Kp=0.25, Kd=1.2)\nDamped — much smoother!'),
    ]
    for ax, data, color, title in pairs:
        ax.plot(data['time'], data['distance'], color=color, lw=2.5)
        ax.axhline(target, color=C_target, linestyle='--', lw=2)
        ax.fill_between(data['time'], target - 1, target + 1,
                        alpha=0.1, color='green')
        ax.set(xlabel='Time (s)', title=title, ylim=[0, 35])

    axes[0].set_ylabel('Distance (cm)')
    plt.suptitle('Adding Derivative (D) Damps Oscillation',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.show()


def plot_kd_explore(data, kd_value, kp_value, target):
    """PD explore: distance + P and D terms stacked."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 6), sharex=True)

    ax1.plot(data['time'], data['distance'], color=C_D, lw=2.5)
    ax1.axhline(target, color=C_target, linestyle='--', lw=2)
    ax1.fill_between(data['time'], target - 1, target + 1, alpha=0.12, color='green')
    ax1.set(ylabel='Distance (cm)',
            title=f'PD Control  Kp={kp_value}  Kd={kd_value}', ylim=[0, 35])

    ax2.plot(data['time'], data['D'], color=C_D, lw=2, label=f'D term (Kd={kd_value})')
    ax2.plot(data['time'], data['P'], color=C_P, lw=2, label='P term', alpha=0.7)
    ax2.axhline(0, color='k', lw=0.8)
    ax2.set(xlabel='Time (s)', ylabel='Term value', ylim=[-1.2, 1.2])
    ax2.legend()

    plt.tight_layout()
    plt.show()


# ── Part 7 ────────────────────────────────────────────────────────────────────

def plot_pid_contributions(data, target):
    """Three-panel: distance, stacked throttle contributions, individual terms."""
    t = data['time']
    p, i_v, d_v = data['P'], data['I'], data['D']

    fig, axes = plt.subplots(3, 1, figsize=(13, 9), sharex=True)

    axes[0].plot(t, data['distance'], color=C_PID, lw=2.5, label='Distance (PID)')
    axes[0].axhline(target, color=C_target, linestyle='--', lw=2, label='Target')
    axes[0].set(ylabel='Distance (cm)',
                title='Full PID: Distance reaches target and holds', ylim=[4, 35])
    axes[0].legend()

    axes[1].plot(t, data['throttle'], 'k', lw=2.0, label='Total throttle', zorder=10)
    axes[1].fill_between(t, 0, p,               alpha=0.4, color=C_P, label='P term')
    axes[1].fill_between(t, p, p + i_v,          alpha=0.4, color=C_I, label='I term (stacked)')
    axes[1].fill_between(t, p + i_v, data['throttle'],
                         alpha=0.4, color=C_D, label='D term (stacked)')
    axes[1].axhline(0, color='k', lw=0.8)
    axes[1].set(ylabel='Throttle',
                title='P + I + D contributions to total throttle', ylim=[-1.4, 1.4])
    axes[1].legend(ncol=4, fontsize=9)

    axes[2].plot(t, p,   color=C_P, lw=2, label='P = Kp × error')
    axes[2].plot(t, i_v, color=C_I, lw=2, label='I = Ki × integral')
    axes[2].plot(t, d_v, color=C_D, lw=2, label='D = Kd × derivative')
    axes[2].axhline(0, color='k', lw=0.8)
    axes[2].set(xlabel='Time (s)', ylabel='Term value',
                title='Individual P, I, D terms over time')
    axes[2].legend(ncol=3)

    plt.suptitle('Inside Full PID: Three Terms Working Together',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.show()


def plot_grand_comparison(datasets, target):
    """2×2 grid: P / PI / PD / PID all with same disturbance.

    datasets: list of (data, label, kp, ki, kd, color, desc)
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    axes = axes.flatten()

    for ax, (data, label, kp, ki, kd, color, desc) in zip(axes, datasets):
        ax.plot(data['time'], data['distance'], color=color, lw=2.5)
        ax.axhline(target, color=C_target, linestyle='--', lw=2)
        ax.fill_between(data['time'], target - 0.5, target + 0.5,
                        alpha=0.12, color='green')
        final_err = abs(data['error'][-1])
        settled   = np.where(np.abs(data['error']) < 0.5)[0]
        settle_t  = f'{data["time"][settled[0]]:.0f}s' if len(settled) else 'never'
        ax.set(xlabel='Time (s)', ylabel='Distance (cm)', ylim=[4, 35],
               title=f'{label}  (Kp={kp}, Ki={ki}, Kd={kd})\n{desc}')
        ax.text(0.02, 0.08,
                f'Final error: {final_err:.2f} cm  |  Settles: {settle_t}',
                transform=ax.transAxes, fontsize=9,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    plt.suptitle(
        'Grand Comparison: P vs PI vs PD vs PID\n'
        '(all simulations have same disturbance — constant force away from wall)',
        fontsize=12, fontweight='bold',
    )
    plt.tight_layout()
    plt.show()


def plot_pid_tune(data, kp, ki, kd, target):
    """Full PID tuning view: distance + all three terms + score."""
    t = data['time']

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 7), sharex=True)

    ax1.plot(t, data['distance'], color=C_PID, lw=2.5, label='Distance')
    ax1.axhline(target, color=C_target, linestyle='--', lw=2,
                label=f'Target {target} cm')
    ax1.fill_between(t, target - 0.5, target + 0.5,
                     alpha=0.15, color='green', label='±0.5 cm')
    ax1.set(ylabel='Distance (cm)',
            title=f'Your PID: Kp={kp}  Ki={ki}  Kd={kd}', ylim=[4, 35])
    ax1.legend()

    ax2.plot(t, data['P'],        color=C_P, lw=2,   label=f'P (Kp={kp})')
    ax2.plot(t, data['I'],        color=C_I, lw=2,   label=f'I (Ki={ki})')
    ax2.plot(t, data['D'],        color=C_D, lw=2,   label=f'D (Kd={kd})')
    ax2.plot(t, data['throttle'], color='k', lw=1.5, label='Total', linestyle='--')
    ax2.axhline(0, color='k', lw=0.8)
    ax2.set(xlabel='Time (s)', ylabel='Term / Throttle', ylim=[-1.4, 1.4])
    ax2.legend(ncol=4, fontsize=9)

    plt.tight_layout()
    plt.show()

    settled_idx = np.where(np.abs(data['error']) < 0.5)[0]
    settle_time = t[settled_idx[0]] if len(settled_idx) else t[-1]
    final_err   = abs(data['error'][-1])
    max_over    = max(0, target - min(data['distance']))
    score       = 100 - (settle_time * 2) - (final_err * 15) - (max_over * 5)

    print(f'Kp={kp}  Ki={ki}  Kd={kd}')
    print(f'  Settle time (within 0.5 cm) : {settle_time:.1f}s')
    print(f'  Final error                 : {final_err:.2f} cm')
    print(f'  Max overshoot below target  : {max_over:.2f} cm')
    print(f'  Score (higher = better)     : {score:.0f}')