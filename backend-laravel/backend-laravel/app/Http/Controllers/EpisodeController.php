<?php

namespace App\Http\Controllers;

use App\Models\Episode;
use App\Services\AuditService;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Barryvdh\DomPDF\Facade\Pdf;


class EpisodeController extends Controller
{
    // Дашборд Врача
    public function doctorIndex()
    {
        $user = Auth::user();
        
        $myStats = Episode::where('user_id', $user->id)
            ->selectRaw('AVG(quality_score) as avg_score, COUNT(*) as total')
            ->first();
        
        $episodes = Episode::where('user_id', $user->id)->latest()->paginate(10);
        
        return view('dashboard.doctor', compact('episodes', 'myStats'));
    }

    public function chiefIndex()
    {
        $doctorsStats = DB::table('episodes')
            ->join('users', 'episodes.user_id', '=', 'users.id')
            ->select('users.name', DB::raw('AVG(episodes.quality_score) as avg_score'), DB::raw('COUNT(episodes.id) as total'))
            ->groupBy('users.id', 'users.name')
            ->orderBy('avg_score', 'desc')
            ->get();

        $episodes = Episode::with('user')->latest()->paginate(15);
        
        return view('dashboard.chief', compact('doctorsStats', 'episodes'));
    }

    public function store(Request $request, AuditService $auditService)
    {
        $request->validate([
            'files' => 'required|array',
            'files.*' => 'required|mimes:pdf|max:10240' // Каждый файл макс 10MB
        ]);

        $files = $request->file('files');
        $successCount = 0;
        $failCount = 0;
        $errors = [];

        foreach ($files as $file) {
            try {
                $path = $file->store('epicrisis');

                $episode = Episode::create([
                    'user_id' => Auth::id(),
                    'filename' => $file->getClientOriginalName(),
                    'status' => 'pending',
                    'file_path' => $path,
                ]);

                $result = $auditService->analyze($file);

                // Обновляем результат
                $episode->update([
                    'diagnosis_code' => $result['diagnosis'] ?? 'Unknown',
                    'quality_score' => $result['quality_score'] ?? 0,
                    'extracted_facts' => $result['extracted_facts'] ?? [],
                    'check_results' => $result['results'] ?? [],
                    'status' => 'completed'
                ]);

                $successCount++;

            } catch (\Exception $e) {
                $failCount++;
                $errors[] = "Ошибка в файле {$file->getClientOriginalName()}: " . $e->getMessage();
                
                if (isset($episode)) {
                    $episode->update(['status' => 'failed']);
                }
            }
        }

        $message = "Обработано файлов: " . count($files) . ". Успешно: {$successCount}.";
        if ($failCount > 0) {
            $message .= " Ошибок: {$failCount}.";
        }

        return redirect()->back()->with('success', $message)->withErrors($errors);
    }

    public function show(Episode $episode)
    {
        if (Auth::id() !== $episode->user_id && !Auth::user()->isChief()) {
            abort(403);
        }
        return view('episodes.show', compact('episode'));
    }

    public function download(Episode $episode)
    {
        if (Auth::id() !== $episode->user_id && !Auth::user()->isChief()) {
            abort(403);
        }

        return Storage::download($episode->file_path, $episode->filename);
    }
    
    public function destroy(Episode $episode)
    {
        if (Auth::id() !== $episode->user_id && !Auth::user()->isChief()) {
            abort(403);
        }

        if ($episode->file_path && Storage::exists($episode->file_path)) {
            Storage::delete($episode->file_path);
        }

        $episode->delete();

        return redirect()->back()->with('success', 'Эпикриз успешно удален.');
    }
    
    public function export(Episode $episode)
    {
        if (Auth::id() !== $episode->user_id && !Auth::user()->isChief()) {
            abort(403);
        }

        $data = [
            'episode' => $episode,
        ];

        $pdf = Pdf::loadView('episodes.report', $data);
        
        $filename = "Otchet_{$episode->diagnosis_code}_" . date('d.m.Y') . ".pdf";

        return $pdf->download($filename);
    }
}