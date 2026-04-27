import click
from flask.cli import with_appcontext
from app import db
from app.models import User


def register_commands(app):
    app.cli.add_command(create_superuser)
    app.cli.add_command(list_users)
    app.cli.add_command(delete_user)
    app.cli.add_command(promote_user)


@click.command("create-superuser")
@click.option("--username", prompt="Username", help="Superuser username")
@click.password_option("--password", help="Superuser password (min 8 chars)")
@with_appcontext
def create_superuser(username, password):
    """Create a new super user account."""
    username = username.strip()

    if len(username) < 3:
        raise click.BadParameter("Username must be at least 3 characters.", param_hint="username")

    if len(password) < 8:
        raise click.BadParameter("Password must be at least 8 characters.", param_hint="password")

    existing = User.query.filter_by(username=username).first()
    if existing:
        if existing.is_superuser:
            click.echo(click.style(f"[!] '{username}' is already a super user.", fg="yellow"))
        else:
            if click.confirm(f"User '{username}' exists but is not a super user. Promote them?"):
                existing.is_superuser = True
                existing.set_password(password)
                db.session.commit()
                click.echo(click.style(f"[✓] '{username}' promoted to super user and password updated.", fg="green"))
            else:
                click.echo("Aborted.")
        return

    user = User(username=username, is_superuser=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(click.style(f"[✓] Super user '{username}' created successfully.", fg="green"))


@click.command("list-users")
@with_appcontext
def list_users():
    """List all registered users."""
    users = User.query.order_by(User.username).all()
    if not users:
        click.echo("No users found.")
        return
    click.echo(f"{'ID':<6} {'Username':<24} {'Role':<12} {'Wishes'}")
    click.echo("-" * 54)
    for u in users:
        role = click.style("superuser", fg="cyan") if u.is_superuser else "user"
        click.echo(f"{u.id:<6} {u.username:<24} {role:<12} {len(u.wish_items)}")


@click.command("delete-user")
@click.argument("username")
@with_appcontext
def delete_user(username):
    """Delete a user by USERNAME."""
    user = User.query.filter_by(username=username).first()
    if not user:
        click.echo(click.style(f"[!] User '{username}' not found.", fg="red"))
        return
    if user.is_superuser:
        click.echo(click.style(f"[!] '{username}' is a super user. Use --force to delete super users.", fg="yellow"))
        return
    if click.confirm(f"Delete user '{username}' and all their data?"):
        db.session.delete(user)
        db.session.commit()
        click.echo(click.style(f"[✓] User '{username}' deleted.", fg="green"))
    else:
        click.echo("Aborted.")


@click.command("promote-user")
@click.argument("username")
@with_appcontext
def promote_user(username):
    """Promote an existing user to super user."""
    user = User.query.filter_by(username=username).first()
    if not user:
        click.echo(click.style(f"[!] User '{username}' not found.", fg="red"))
        return
    if user.is_superuser:
        click.echo(click.style(f"[!] '{username}' is already a super user.", fg="yellow"))
        return
    user.is_superuser = True
    db.session.commit()
    click.echo(click.style(f"[✓] '{username}' is now a super user.", fg="green"))
