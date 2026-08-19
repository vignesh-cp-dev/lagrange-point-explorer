from manim import *
import numpy as np

from physics import (
    EARTH_MOON,
    calculate_lagrange_points,
    calculate_mu,
    classify_lagrange_points,
    simulate_satellite,
)


# ------------------------------------------------------------
# Visual configuration
# ------------------------------------------------------------

BG = "#050910"
CYAN = "#20D9FF"
GREEN = "#52E59A"
ORANGE = "#FF8A3D"
WHITE = "#EAF2F7"
MUTED = "#7F94A3"


class LagrangeExplorer(Scene):

    def construct(self):
        self.camera.background_color = BG

        # Physics
        system = EARTH_MOON
        mu = calculate_mu(system)
        points = calculate_lagrange_points(system)
        stability = classify_lagrange_points(system)

        # Map normalized barycentric coordinates into a compact screen region.
        scale_x = 3.2
        scale_y = 2.2

        def to_screen(point):
            x, y = point
            return np.array([(x - 0.5) * scale_x, y * scale_y, 0])

        # ----------------------------------------------------
        # Scene 1 — Opening
        # ----------------------------------------------------

        title = Text(
            "LAGRANGE POINTS",
            font_size=48,
            weight=BOLD,
            color=WHITE,
        )

        subtitle = Text(
            "Equilibrium in a two-body gravitational system",
            font_size=24,
            color=MUTED,
        )

        title.to_edge(UP, buff=1.15)
        subtitle.next_to(title, DOWN, buff=0.35)

        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=DOWN * 0.2))
        self.wait(1)

        self.play(
            title.animate.scale(0.65).to_edge(UP, buff=0.45),
            subtitle.animate.scale(0.75).next_to(title, DOWN, buff=0.22),
        )
        self.wait(1)

        self.play(
        FadeOut(title),
        FadeOut(subtitle),
        )

        # ----------------------------------------------------
        # Scene 2 — Earth / Moon system
        # ----------------------------------------------------

        earth = Dot(
            point=to_screen([-mu, 0.0]),
            radius=0.22,
            color=BLUE,
        )

        moon = Dot(
            point=to_screen([1.0 - mu, 0.0]),
            radius=0.10,
            color=GREY_B,
        )

        earth_label = Text(
            "EARTH",
            font_size=18,
            color=WHITE,
        ).next_to(earth, DOWN + LEFT * 0.35, buff=0.32)

        moon_label = Text(
            "MOON",
            font_size=16,
            color=WHITE,
        ).next_to(moon, DOWN + RIGHT * 0.35, buff=0.32)

        separation_line = DashedLine(
            earth.get_center(),
            moon.get_center(),
            color=MUTED,
            dash_length=0.12,
        )

        barycenter = Dot(
            point=to_screen([0.0, 0.0]),
            radius=0.055,
            color=YELLOW,
        )

        bary_label = Text(
            "BARYCENTER",
            font_size=14,
            color=YELLOW,
        ).next_to(barycenter, UP, buff=0.15)

        self.play(
            FadeIn(earth, scale=0.5),
            FadeIn(moon, scale=0.5),
            Write(earth_label),
            Write(moon_label),
        )

        self.play(Create(separation_line))

        self.play(
            FadeIn(barycenter, scale=0.5),
            Write(bary_label),
        )

        system_label = Text(
            "EARTH — MOON SYSTEM",
            font_size=22,
            color=CYAN,
        ).to_edge(LEFT).shift(DOWN * 0.7)

        self.play(FadeIn(system_label))

        self.wait(1)

        # ----------------------------------------------------
        # Scene 3 — Orbit
        # ----------------------------------------------------

        orbit = Ellipse(
            width=6.5,
            height=2.4,
            color=CYAN,
            stroke_width=2,
            stroke_opacity=0.65,
        )

        self.play(Create(orbit))

        orbit_caption = Text(
            "ROTATING REFERENCE FRAME",
            font_size=17,
            color=MUTED,
        ).to_edge(DOWN)

        self.play(FadeIn(orbit_caption))

        # Move the bodies around the orbit for visual context.
        moon_path = TracedPath(
            moon.get_center,
            stroke_color=CYAN,
            stroke_width=2,
        )

        self.add(moon_path)

        self.play(
            Rotate(
                VGroup(earth, moon, earth_label, moon_label, separation_line),
                angle=PI / 3,
                about_point=barycenter.get_center(),
            ),
            run_time=2,
        )

        self.wait(0.5)

        # ----------------------------------------------------
        # Scene 4 — Five Lagrange points
        # ----------------------------------------------------

        self.play(
            FadeOut(orbit_caption),
            FadeOut(system_label),
            FadeOut(bary_label),
        )

        # Put bodies back into the normalized rotating-frame configuration.
        earth.move_to(to_screen([-mu, 0.0]))
        moon.move_to(to_screen([1.0 - mu, 0.0]))

        earth_label.next_to(earth, DOWN + LEFT * 0.35, buff=0.32)
        moon_label.next_to(moon, DOWN + RIGHT * 0.35, buff=0.32)

        separation_line.put_start_and_end_on(
            earth.get_center(),
            moon.get_center(),
        )

        barycenter.move_to(to_screen([0.0, 0.0]))

        point_mobjects = {}

        for point_id in ["L1", "L2", "L3", "L4", "L5"]:

            pos = to_screen(points[point_id])

            color = (
                GREEN
                if stability[point_id] == "stable"
                else ORANGE
            )

            marker = VGroup(
                Circle(
                    radius=0.10,
                    color=color,
                    stroke_width=2,
                ),
                Dot(
                    radius=0.035,
                    color=color,
                ),
            )

            marker.move_to(pos)

            label = Text(
                point_id,
                font_size=16,
                color=color,
            )

            label_direction = {
                "L1": DOWN,
                "L2": UP,
                "L3": DOWN,
                "L4": RIGHT,
                "L5": RIGHT,
            }[point_id]
            label.next_to(marker, label_direction, buff=0.20)

            point_mobjects[point_id] = VGroup(marker, label)

            self.play(
                FadeIn(marker, scale=0.5),
                Write(label),
                run_time=0.35,
            )

        # Triangle connecting L4 and L5
        triangle = Polygon(
            to_screen(points["L4"]),
            earth.get_center(),
            moon.get_center(),
            color=MUTED,
            stroke_width=1,
            stroke_opacity=0.35,
        )

        self.play(Create(triangle), run_time=0.8)

        explanation = Text(
            "Five equilibrium solutions exist",
            font_size=20,
            color=WHITE,
        ).to_edge(DOWN, buff=0.45)

        self.play(FadeIn(explanation))
        self.wait(1)

        # ----------------------------------------------------
        # Scene 5 — Stability classification
        # ----------------------------------------------------

        self.play(
            FadeOut(explanation),
            FadeOut(triangle),
        )

        stability_title = Text(
            "NOT ALL LAGRANGE POINTS ARE STABLE",
            font_size=28,
            color=WHITE,
        ).to_edge(UP, buff=0.35)

        self.play(Write(stability_title))

        unstable_box = RoundedRectangle(
            width=4.4,
            height=1.15,
            corner_radius=0.12,
            color=ORANGE,
        )

        unstable_text = VGroup(
            Text("L1  •  L2  •  L3", font_size=25, color=ORANGE),
            Text("UNSTABLE", font_size=18, color=ORANGE),
        ).arrange(DOWN, buff=0.08)

        unstable_group = VGroup(
            unstable_box,
            unstable_text,
        ).move_to(LEFT * 2.65 + DOWN * 2.55)

        stable_box = RoundedRectangle(
            width=4.4,
            height=1.15,
            corner_radius=0.12,
            color=GREEN,
        )

        stable_text = VGroup(
            Text("L4  •  L5", font_size=25, color=GREEN),
            Text("STABLE", font_size=18, color=GREEN),
        ).arrange(DOWN, buff=0.08)

        stable_group = VGroup(
            stable_box,
            stable_text,
        ).move_to(RIGHT * 2.65 + DOWN * 2.55)

        self.play(
            FadeIn(unstable_group, shift=LEFT * 0.3),
            FadeIn(stable_group, shift=RIGHT * 0.3),
        )

        self.wait(1)

        # ----------------------------------------------------
        # Scene 6 — L1 perturbation
        # ----------------------------------------------------

        self.play(
            FadeOut(stability_title),
            FadeOut(unstable_group),
            FadeOut(stable_group),
        )

        diagram_shift = DOWN * 0.45
        VGroup(
            earth,
            moon,
            earth_label,
            moon_label,
            separation_line,
            barycenter,
            orbit,
            moon_path,
            *point_mobjects.values(),
        ).shift(diagram_shift)

        l1_title = Text(
            "L1 — UNSTABLE",
            font_size=30,
            color=ORANGE,
        ).to_edge(UP, buff=0.35)

        self.play(Write(l1_title))

        l1_pos = to_screen(points["L1"]) + diagram_shift

        satellite = Dot(
            point=l1_pos,
            radius=0.09,
            color=YELLOW,
        )

        sat_label = Text(
            "SATELLITE",
            font_size=14,
            color=YELLOW,
        ).next_to(satellite, UP, buff=0.1)

        self.play(
            FadeIn(satellite, scale=0.5),
            Write(sat_label),
        )

        perturb_arrow = Arrow(
            satellite.get_center(),
            satellite.get_center() + RIGHT * 0.8,
            color=ORANGE,
            buff=0,
        )

        self.play(GrowArrow(perturb_arrow))

        self.play(
            satellite.animate.shift(RIGHT * 2.0 + UP * 0.7),
            sat_label.animate.shift(RIGHT * 2.0 + UP * 0.7),
            run_time=2,
        )

        escape_text = Text(
            "SMALL PERTURBATION → DRIFT",
            font_size=20,
            color=ORANGE,
        ).to_edge(DOWN, buff=0.45)

        self.play(FadeIn(escape_text))
        self.wait(1)

        # ----------------------------------------------------
        # Scene 7 — L4 libration
        # ----------------------------------------------------

        self.play(
            FadeOut(l1_title),
            FadeOut(perturb_arrow),
            FadeOut(escape_text),
            FadeOut(satellite),
            FadeOut(sat_label),
        )

        l4_title = Text(
            "L4 — STABLE LIBRATION",
            font_size=30,
            color=GREEN,
        ).to_edge(UP, buff=0.35)

        self.play(Write(l4_title))

        l4_pos = to_screen(points["L4"]) + diagram_shift

        satellite.move_to(l4_pos)

        sat_label = Text(
            "SATELLITE",
            font_size=14,
            color=YELLOW,
        ).next_to(satellite, UP, buff=0.1)

        self.play(
            FadeIn(satellite, scale=0.5),
            Write(sat_label),
        )

        # Drive the visible libration from the same RK4 model used by physics.py.
        initial_position = points["L4"] + np.array([0.035, -0.02])
        initial_velocity = np.array([0.0, 0.02])
        trajectory = simulate_satellite(
            system,
            initial_position,
            initial_velocity,
            duration=16.0,
            dt=0.02,
        )
        trajectory_points = [
            to_screen(position) + diagram_shift
            for position in trajectory[::4, :2]
        ]
        libration_path = VMobject(color=YELLOW, stroke_width=2.5)
        libration_path.set_points_smoothly(trajectory_points)

        satellite.move_to(trajectory_points[0])
        sat_label.next_to(satellite, UP, buff=0.12)

        def follow_satellite(label):
            label.next_to(satellite, UP, buff=0.12)

        sat_label.add_updater(follow_satellite)

        self.play(Create(libration_path), run_time=1)

        self.play(
            MoveAlongPath(satellite, libration_path),
            run_time=4,
        )

        sat_label.remove_updater(follow_satellite)
        sat_label.next_to(satellite, UP, buff=0.12)

        stable_text = Text(
            "PERTURBATION  •  LIBRATION  •  CONFINED",
            font_size=20,
            color=GREEN,
        ).to_edge(DOWN, buff=0.45)

        self.play(FadeIn(stable_text))

        self.wait(1)

        # ----------------------------------------------------
        # Scene 8 — Final summary
        # ----------------------------------------------------

        self.play(
            FadeOut(l4_title),
            FadeOut(libration_path),
            FadeOut(stable_text),
            FadeOut(satellite),
            FadeOut(sat_label),
            FadeOut(point_mobjects["L1"]),
            FadeOut(point_mobjects["L2"]),
            FadeOut(point_mobjects["L3"]),
            FadeOut(point_mobjects["L4"]),
            FadeOut(point_mobjects["L5"]),
            FadeOut(earth),
            FadeOut(moon),
            FadeOut(earth_label),
            FadeOut(moon_label),
            FadeOut(separation_line),
            FadeOut(barycenter),
            FadeOut(moon_path),
            FadeOut(orbit),
        )

        final_title = Text(
            "LAGRANGE POINTS",
            font_size=42,
            color=WHITE,
        )

        final_title.to_edge(UP)

        final_unstable = Text(
            "L1    L2    L3",
            font_size=28,
            color=ORANGE,
        )

        final_stable = Text(
            "L4    L5",
            font_size=28,
            color=GREEN,
        )

        final_body = VGroup(
            final_unstable,
            final_stable,
        ).arrange(DOWN, buff=0.35)

        final_labels = VGroup(
            Text("UNSTABLE", font_size=18, color=ORANGE),
            Text("STABLE", font_size=18, color=GREEN),
        ).arrange(DOWN, buff=0.58).next_to(final_body, RIGHT, buff=0.55)

        method = Text(
            "CR3BP  •  NUMPY  •  RK4",
            font_size=18,
            color=CYAN,
        ).next_to(final_body, DOWN, buff=0.7)

        self.play(
            Write(final_title),
            FadeIn(final_body, shift=UP * 0.2),
            FadeIn(final_labels, shift=RIGHT * 0.2),
        )

        self.play(FadeIn(method))

        self.wait(3)