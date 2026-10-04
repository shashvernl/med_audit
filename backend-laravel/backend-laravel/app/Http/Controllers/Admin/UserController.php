<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Gate;

class UserController extends Controller
{
    public function index()
    {
        if (!auth()->user()->isChief()) {
            abort(403);
        }

        $users = User::where('id', '!=', auth()->id())->paginate(10); // Не показываем самого себя
        return view('admin.users.index', compact('users'));
    }

    public function updateRole(Request $request, User $user)
    {
        if (!auth()->user()->isChief()) {
            abort(403);
        }

        $request->validate([
            'role' => 'required|in:doctor,chief'
        ]);

        $user->update(['role' => $request->role]);

        return back()->with('success', 'Роль пользователя обновлена.');
    }
    
    public function destroy(User $user)
    {
         if (!auth()->user()->isChief()) {
            abort(403);
        }
        
        if ($user->id === auth()->id()) {
            return back()->withErrors(['error' => 'Нельзя удалить свой аккаунт.']);
        }

        $user->delete();
        return back()->with('success', 'Пользователь удален.');
    }
}